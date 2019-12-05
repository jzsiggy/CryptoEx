const submitBtn = document.querySelector(".submit-btn");

const ctx = document.getElementById('myChart').getContext('2d');
const chart = new Chart(ctx, {
  type: 'line',
  data : {
    labels : [],
    datasets : [
      {
        label: "Prediction",
        data: [],
        backgroundColor: 'rgba(0, 0, 0, 0)',
        borderColor: 'rgba(153, 126, 252, 0.7)'
      },
      {
        label: "Price",
        data: [],
        backgroundColor: 'rgba(0, 0, 0, 0)',
        borderColor: 'rgba(255, 99, 132, 1)'
      }
    ],
  }
});


submitBtn.addEventListener("click", () => {
  
  const coin = document.querySelector("#coin-selector")
  const regressor = document.querySelector("#model-selector")
  const timeStep = document.querySelector("#time-step-selector")

  const postObj = {
    "coin" : coin.value,
    "regressor" : regressor.value,
    "timeStep" : timeStep.value,
  };

  postJson = JSON.stringify(postObj);
  postJson = JSON.parse(postJson);
  
  axios.post("http://127.0.0.1:5000/api", postJson)
  .then(response => {
    data = response.data;

    predData = data.pred;
    actualData = data.actual;

    chart.data.labels = predData;
    chart.data.datasets[0].data = predData;
    chart.data.datasets[1].data = actualData;
    chart.update();
    
  });
});