const mongoose = require('mongoose');

const recommendationSchema = new mongoose.Schema({
  user: { type: mongoose.Schema.Types.ObjectId, ref: 'User' },
  type: { type: String, enum: ['fitness', 'nutrition', 'mental'] },
  content: String,
  feedback: { type: String, default: null },
}, { timestamps: true });

module.exports = mongoose.model('Recommendation', recommendationSchema);
