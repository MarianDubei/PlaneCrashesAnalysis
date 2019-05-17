class App extends React.Component {
  static getDerivedStateFromProps(props, state) {
    // load data with ajax
  }
  load() {
    loading();
  }
  render() {
    return (
            React.createElement("div", null, React.createElement("h2", {style:{color: "white", webkitTextStroke: "0.7px #1a1a1a"}, className:"text-center"}, "What {} you need to check?".replace("{}", window.buttonValue)), React.createElement("form", {action:"/analyze", method:"post"}, React.createElement("div", {className:"form-group col-sm-4 col-sm-offset-4"}, React.createElement("input", {className:"form-control", placeholder:"Enter here", type:"text", name:"criteria"})), React.createElement("input", {className:"form-control hidden", type:"text", name:"button", value:window.buttonValue}), React.createElement("button", {className:"btn btn-primary", onClick:this.load, type:"submit"}, "Submit"))));            
  }}
// React.createElement("input", {type:"submit", name:"submit", value:"Submit"})


function renderReact() {
  ReactDOM.render(
  React.createElement(App, null),
  document.getElementById('root'));

}
window.buttonValue = ""

$(document).on("click", ".aircraft", function () {
  window.buttonValue = "aircraft";
  renderReact();
});

$(document).on("click", ".year", function () {
  window.buttonValue = "year";
  renderReact();
});

$(document).on("click", ".airline", function () {
  window.buttonValue = "airline";
  renderReact();
});
