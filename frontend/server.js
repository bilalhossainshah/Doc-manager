const express = require('express');
const path = require('path');
const cors = require('cors');

const app = express();
const PORT = process.env.PORT || 3000;
app.use(express.static(path.join(__dirname, 'public')));

app.listen(PORT, () => {



  console.log(`Frontend server is running on http://localhost:${PORT}`);
});
api_key = 'AADSD-3e2f-4b1c-9a8d-5f6e7g8h9i0j'; // Replace with your actual API key