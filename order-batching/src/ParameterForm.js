import { useState } from 'react'

function ParameterForm() {
  const [orderNumber, setName] = useState("")
  
  const downloadTextFile = () => {
    const element = document.createElement('a')
    const file = new Blob([document.getElementById('input').value],{type:"text/plain;charset=utf-8"})
    element.href = URL.createObjectURL(file)
    element.download = "myFile.txt"
    document.body.appendChild(element)
    element.click()
    }

  let orders = []

  if (orderNumber){
    orders = Array.from({length: orderNumber}, (_, index) => {
        return (
        <div>
            <label>{index+1}: </label>
            <input type ="number" id="input" key={index+1} placeholder="capacity"/>
            <br/>
        </div>
        );
    });
  } 


  return (
    <div>
        <form>
            <h1>Maximal Capacity and Order Number</h1>
            <input id="input" type="number" value={orderNumber} onChange={(e) => setName(e.target.value)} />
            {orders}
        </form>  

        <button onClick={downloadTextFile}>Submit</button>
    </div>
  );
}

export default ParameterForm;