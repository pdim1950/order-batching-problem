const express = require("express");
const path = require('path');
const requestRoutes = require('./routes/api');
const bodyParser = require('body-parser')

const app = express();
const port = 8000;

app.set('view engine', 'ejs');
app.use(express.static(path.join(__dirname, 'public')));


app.use(bodyParser.json());
app.use(bodyParser.urlencoded({ extended: true }));

app.use('/', requestRoutes);

app.listen(port, () => {
    console.log(`Server running on port ${port}`);
})