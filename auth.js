const jwt = require('jsonwebtoken');

function verifyToken(req, res, next) {
  const authHeader = req.headers['authorization'];
  if (!authHeader) return res.status(401).json({ error: 'Access token missing' });

  const token = authHeader.split(' ')[1]; // Extract token from "Bearer <TOKEN>"

  jwt.verify(token, process.env.SUPABASE_JWT_SECRET, { algorithms: ['HS256'] }, (err, user) => {
    if (err) return res.status(403).json({ error: 'Invalid or expired token' });
    req.userId = user.sub; // Extract User ID from token payload
    next();
  });
}

module.exports = verifyToken;