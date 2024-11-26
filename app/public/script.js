var j = [];
let count = 1;
let capacityInput = document.getElementById("capacity");
let maxCapacity = document.getElementById("maxCapacity");
let text = document.getElementById("text");
let added = document.getElementById("added");
const form = document.getElementById("algo");
document.getElementById('parameter').style.display= "none";
const alg = document.getElementById("algorithms");
const done = document.getElementById("done");
const reset = document.getElementById("reset");
const sub = document.getElementById("submit");

let lam_i = document.getElementById("c_span_lam_i")
let mu_i = document.getElementById("c_span_mu_i")
let t_i = document.getElementById("c_span_t_i")

let pop_i = document.getElementById("c_span_pop_i")
let gen_i = document.getElementById("c_span_gen_i")

let pop = 0
let gen = 0
let lam = 0
let mu = 0
let t = 0

done.disabled = true;


text.style.display = "none";
form.style.display = "none";
capacityInput.style.display = "none";
added.style.display = "none";
alg.style.display = "none";
document.getElementById("next").style.display = "none";
reset.style.display = "none";
document.getElementById("c_span").style.display = "none";
document.getElementById("c_span_lam").style.display = "none";
document.getElementById("c_span_mu").style.display = "none";
document.getElementById("c_span_t").style.display = "none";
document.getElementById("c_span_lam_i").style.display = "none";
document.getElementById("c_span_mu_i").style.display = "none";
document.getElementById("c_span_t_i").style.display = "none";

document.getElementById("c_span_pop").style.display = "none";
document.getElementById("c_span_gen").style.display = "none";
document.getElementById("c_span_pop_i").style.display = "none";
document.getElementById("c_span_gen_i").style.display = "none";


lam_i.addEventListener('input', function(event){
  if (lam_i.value == "" || mu_i.value == "" || t_i.value == ""){
    sub.disabled = true;
  } else { sub.disabled = false }
})

mu_i.addEventListener('input', function(event){
  if (mu_i.value == "" || lam_i.value == "" || t_i.value == ""){
    sub.disabled = true;
  } else { sub.disabled = false }
})

t_i.addEventListener('input', function(event){
  if (t_i.value == "" || mu_i.value == "" || lam_i.value == ""){
    sub.disabled = true;
  } else { sub.disabled = false }
})

pop_i.addEventListener('change', function(event){
  if (pop_i.value == "" || gen_i.value == ""){
    sub.disabled = true;
  } else { sub.disabled = false }
})

gen_i.addEventListener('change', function(event){
  if (gen_i.value == "" || pop_i.value == ""){
    sub.disabled = true;
  } else { sub.disabled = false }
})

alg.addEventListener('change', function(event){

  if(alg.value == "ILS"){
    gen_i.value = "";
    pop_i.value = "";
    sub.disabled = true;
    j[0] = { "algorithm" : alg.value , "maxCapacity" : maxCapacity.value, "lam" : lam_i.value, "mu" : mu_i.value, "t" : t_i.value }
    document.getElementById("c_span_lam").style.display = "inline";
    document.getElementById("c_span_mu").style.display = "inline";
    document.getElementById("c_span_t").style.display = "inline";
    document.getElementById("c_span_lam_i").style.display = "inline";
    document.getElementById("c_span_mu_i").style.display = "inline";
    document.getElementById("c_span_t_i").style.display = "inline";

    document.getElementById("c_span_pop").style.display = "none";
    document.getElementById("c_span_gen").style.display = "none";
    document.getElementById("c_span_pop_i").style.display = "none";
    document.getElementById("c_span_gen_i").style.display = "none";

  } else if(alg.value == "GA"){
    lam_i.value = "";
    mu_i.value = "";
    t_i.value = "";
    sub.disabled = true;
    document.getElementById("c_span_pop").style.display = "inline";
    document.getElementById("c_span_gen").style.display = "inline";
    document.getElementById("c_span_pop_i").style.display = "inline";
    document.getElementById("c_span_gen_i").style.display = "inline";

    document.getElementById("c_span_lam").style.display = "none";
    document.getElementById("c_span_mu").style.display = "none";
    document.getElementById("c_span_t").style.display = "none";
    document.getElementById("c_span_lam_i").style.display = "none";
    document.getElementById("c_span_mu_i").style.display = "none";
    document.getElementById("c_span_t_i").style.display = "none";

  } else {
    sub.disabled = false;
    lam_i.value = "";
    mu_i.value = "";
    t_i.value = "";
    gen_i.value = "";
    pop_i.value = "";
    document.getElementById("c_span_lam").style.display = "none";
    document.getElementById("c_span_mu").style.display = "none";
    document.getElementById("c_span_t").style.display = "none";
    document.getElementById("c_span_lam_i").style.display = "none";
    document.getElementById("c_span_mu_i").style.display = "none";
    document.getElementById("c_span_t_i").style.display = "none";

    document.getElementById("c_span_pop").style.display = "none";
    document.getElementById("c_span_gen").style.display = "none";
    document.getElementById("c_span_pop_i").style.display = "none";
    document.getElementById("c_span_gen_i").style.display = "none";
    console.log("hiba")
    console.log(j);
  }
})


capacityInput.addEventListener("input", function(event){
    document.getElementById("next").disabled = false;
});

maxCapacity.addEventListener("input", function(event){
    document.getElementById("done").disabled = false;

});

function show(){
  if(maxCapacity.value < 30 || maxCapacity.value > 100){
    alert("Please enter a maximal capacity between 30 and 100");
  } else {
    maxCapacity.setAttribute('readonly', true);
    form.style.display = "inline";
    capacityInput.style.display = "inline";
    added.style.display = "inline";
    alg.style.display = "inline";
    document.getElementById("next").style.display = "inline";
    reset.style.display = "inline";
    done.style.display = "none";
    document.getElementById("c_span").style.display = "inline";
  
  }
}


function selected(id){
  let d = document.getElementById(id);
  let value = document.getElementById(id).innerText;
  d.style.backgroundColor = "#ac293f";
  d.style.pointerEvents = "none";
  let text = document.getElementById("text");
  text.value += value + " ";
}

function next(){

  let capacity = Number(document.getElementById("capacity").value);
  let maxCapacity = Number(document.getElementById("maxCapacity").value);

  if(capacity > maxCapacity){
    alert("The capacity of an order can not be greater then the maximal capacity");
  } else if(text.value==''){
    alert("Please select some items from the warehouse (click on them)");
  } else {
    added.value += count.toString() + ": " + text.value + "  capacity: " + capacity.toString() + "\n";
    let reset = text.value.split(" ");
    text.value = "";

    let coordinates = ""

    for (let i = 0; i < reset.length-1; i++) {
      if(i==reset.length-2){
        coordinates += reset[i];
      } else {
        coordinates += reset[i] + ",";
      }
    }

    coordinates = coordinates.split("(").join('').split(")").join('').split(",");
    order = { "number" : count, "customer" : count, "coordinates" : coordinates, "capacity" : capacity }

    for (let i = 0; i < reset.length-1; i++) {
      document.getElementById(reset[i]).style.pointerEvents = "auto";
      document.getElementById(reset[i]).style.backgroundColor = "#e4c515";
    }
    document.getElementById("capacity").value = "";
    document.getElementById("next").disabled = true;
    j[count] = order;
    count += 1;
  }
}

form.addEventListener('submit', function(event){
  if(alg.value === "ILS"){
    j[0] = { "algorithm" : alg.value , "maxCapacity" : maxCapacity.value, "lam" : lam_i.value, "mu" : mu_i.value, "t" : t_i.value }
  } else if(alg.value === "GA"){
    j[0] = { "algorithm" : alg.value , "maxCapacity" : maxCapacity.value, "pop" : pop_i.value, "gen" : gen_i.value }
  } else {
    j[0] = { "algorithm" : alg.value , "maxCapacity" : maxCapacity.value }
  }
  document.getElementById("parameter").value = JSON.stringify(j)
})

