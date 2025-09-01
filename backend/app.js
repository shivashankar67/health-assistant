const express = require('express');
const cors = require('cors');
const dotenv = require('dotenv');

dotenv.config();

const app = express();
app.use(cors());
app.use(express.json());
const authRoutes = require('./routes/auth');
app.use('/api/auth', authRoutes);

// Routes
app.get('/', (req, res) => {
  res.json({ message: "AI Health Assistant Backend is running 🚀" });
});


module.exports = app;
