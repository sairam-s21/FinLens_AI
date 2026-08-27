require('dotenv').config();
const express = require('express');
const cors = require('cors');
const multer = require('multer');
const { getDocument, extractText } = require('unpdf'); // Native serverless PDF parser
const { createClient } = require('@supabase/supabase-js');
const { spawn } = require('child_process');
const verifyToken = require('./auth');

const app = express();
app.use(cors());
app.use(express.json());

const upload = multer({ storage: multer.memoryStorage() });

// Fail-safe initialization for Supabase
const supabaseUrl = process.env.SUPABASE_URL || '';
const supabaseKey = process.env.SUPABASE_KEY || '';
const supabase = createClient(supabaseUrl, supabaseKey);
// Helper function to execute Python RAG pipeline
const runAiPipeline = (text) => {
  return new Promise((resolve, reject) => {
    // Spawns Python process running your pipeline script
    const pythonProcess = spawn('python3', ['./ai/ai_pipeline.py', text]);

    let resultData = '';
    pythonProcess.stdout.on('data', (data) => {
      resultData += data.toString();
    });

    pythonProcess.stderr.on('data', (err) => {
      console.error('Python Script Error:', err.toString());
    });

    pythonProcess.on('close', (code) => {
      if (code !== 0) return reject(new Error('AI processing failed'));
      try {
        resolve(JSON.parse(resultData)); // Parses JSON printed by Python
      } catch (e) {
        reject(new Error('Invalid JSON output from AI pipeline'));
      }
    });
  });
};
app.get('/', (req, res) => res.json({ message: 'FinLens Backend API Running' }));
app.get('/health', (req, res) => res.json({ status: 'Server is healthy!' }));

app.post('/api/v1/analyze', verifyToken, upload.single('file'), async (req, res) => {
  try {
    if (!req.file) {
      return res.status(400).json({ error: 'No PDF file uploaded' });
    }

    // 1. Extract PDF text cleanly using unpdf
    let pdfText = '';
    try {
      const pdf = await getDocument({ data: new Uint8Array(req.file.buffer) }).promise;
      const { text } = await extractText(pdf);
      pdfText = Array.isArray(text) ? text.join(' ') : text;
    } catch (pdfErr) {
      console.error('PDF Processing Error:', pdfErr.message);
      return res.status(422).json({ error: 'Failed to extract text from PDF buffer' });
    }

    // 2. Execute Python RAG Pipeline
    let aiOutput;
    try {
      aiOutput = await runAiPipeline(pdfText);
    } catch (aiErr) {
      console.error('AI Execution Error:', aiErr.message);
      return res.status(500).json({ error: 'AI pipeline execution failed' });
    }

    // 3. Save to Supabase
    const { data, error } = await supabase.from('invoices').insert([
      {
        user_id: req.userId,
        filename: req.file.originalname,
        total_amount: aiOutput.total_amount,
        risk_score: aiOutput.risk_score,
        risk_level: aiOutput.risk_level,
        audit_flags: aiOutput.audit_flags,
        mcp_refund: aiOutput.mcp_refund
      }
    ]).select();

    if (error) {
      console.error('Database Error:', error.message);
      return res.status(500).json({ error: error.message });
    }

    return res.json({
      status: 'success',
      invoice_id: data[0].id,
      result: aiOutput
    });

  } catch (err) {
    console.error('Unhandled Vercel Route Error:', err.message);
    return res.status(500).json({ error: err.message || 'Internal Server Error' });
  }
});

if (process.env.NODE_ENV !== 'production') {
  const PORT = process.env.PORT || 8000;
  app.listen(PORT, () => console.log(`Server running on port ${PORT}`));
}

module.exports = app;
