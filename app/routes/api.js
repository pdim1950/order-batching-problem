const express = require('express');
var request = require('request-promise'); 

const router = express.Router();

router.get('/', function(req, res) {
    res.render('index');
});

router.post('/batch', async (req, res) => {
  const parameters = JSON.parse(req.body.parameter)
  console.log(parameters);
  var options = {
    method: 'POST',
    uri: 'http://127.0.0.1:5000/batch',
    body: parameters,
    json: true
  }

  var returndata; 
    var sendrequest = await request(options) 
    .then(function (parsedBody) { 
        console.log(parsedBody);
        returndata = parsedBody;
    }) 
    .catch(function (err) { 
        console.log(err); 
    }); 
     
    res.render('result',{result : returndata}); 
  
});

router.get('')
module.exports = router;