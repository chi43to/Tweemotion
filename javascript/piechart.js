var data = [{
  type: "pie",
  values: ["1.0","27","12.0","0.33","5.0","4.0","3.7"],

  labels: ["Positivity","Joy","Fear","Sadness","Anger","Surprise","Disgust"],
  textinfo: "label+percent",
  insidetextorientation: "radial"
}]

var layout = [{
  height: 700,
  width: 700
}]

Plotly.newPlot('test2', data, layout)
