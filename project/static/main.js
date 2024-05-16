// custom javascript

(function() {
  console.log('Sanity Check!');
  document.getElementById('error').style.display = 'none';
})();



function handleSubmit(form) {
  var formAction = form.action;
  var formData = new FormData(form);
  var data={};
  var formBody = [];
  for (const [key, value] of formData) {
    data[key]=value;
    var encodedKey = encodeURIComponent(key);
    var encodedValue = encodeURIComponent(value);
    formBody.push(encodedKey + "=" + encodedValue);

  }
  formBody = formBody.join("&");

  console.log('handleSubmit',formAction,data,formBody)
  fetch(formAction, {
    method: 'POST',
    headers: {'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  })
  .then(response => response.json())
  .then(data => {
    console.log('response.json->',data)
    if (data.task_id){
      getStatus(data.task_id)
    }
    
    const error = document.getElementById('error');
    if (data.error){
      error.innerHTML = data.error;
      error.style.display = 'block';
    }else{
      error.style.display = 'none';
    }

  })
  return false;
}


function handleClick(type) {
  fetch('/tasks', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ type: type }),
  })
  .then(response => response.json())
  .then(data => {
    getStatus(data.task_id)
  })
}

function getStatus(taskID) {
  fetch(`/tasks/${taskID}`, {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json'
    },
  })
  .then(response => response.json())
  .then(res => {
    console.log(res)
    var time = new Date().toLocaleTimeString();
    const html = `
      <tr id='${taskID}'>
        <td>${time}</td>
        <td>${taskID}</td>
        <td>${res.task_status}</td>
        <td>${res.task_result}</td>
      </tr>`;
    var row = document.getElementById(taskID)
    console.log('row', row);
    if (row){
      row.innerHTML = html;
    }else{
      row = document.getElementById('tasks').insertRow(0);
      row.id = taskID;
      row.innerHTML = html;
    }

    const taskStatus = res.task_status;
    if (taskStatus === 'FAILURE'){
      console.log('FAILURE',row);
      row.classList.add("alert-danger")
      return false;
    } 
    if (taskStatus === 'SUCCESS'){ 
      console.log('SUCCESS',row);
      if ( res.task_result !== "None"){
        row.classList.add("alert-success")
      }else{
        row.classList.add("alert-danger")
      }
      
      return false;
    }
      setTimeout(function() {
      getStatus(res.task_id);
    }, 1000);
  })
  .catch(err => console.log(err));
}
