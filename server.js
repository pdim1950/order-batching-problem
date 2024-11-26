const http = require('http')
const port = 8080

const server = http.createServer(function(req,res) {
    res.write('Hello')
    res.end
})

server.listen(port, function(error) {
    if(error) {
        console.log("Error",error)
    } else {
        console.log('Server is listening on port ' + port)
    }
})