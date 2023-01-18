//import logo from './logo.svg';
import './App.css';
import React from "react";
//import ReactDom from "react-dom";

function AddTicker(props) {
  return (
    <label>
      Add Ticker:
      <input type="text" onChange={props.onChange} value={props.value}></input>
      <button onClick={props.onClick}>Add</button>
    </label>
  );
}

class StocksManager extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      stocks: null,
      addTicker: "",
    };

    this.handleTickerChange = this.handleTickerChange.bind(this);
    this.handleAdd = this.handleAdd.bind(this);
    this.updateStocks = this.updateStocks.bind(this);
  }

  componentDidMount() {
    console.log("mounted");
    fetch("/api")
      .then((resp) => resp.json())
      .then((data) => this.setState({stocks: data.data.stocks}));
  }

  onRemove(elm) {
    this.setState({stocks: this.state.stocks.filter(itm => itm !== elm)}, this.updateStocks);
    //this.updateStocks();
  }

  handleAdd(event) {
    this.setState({stocks: this.state.stocks.concat([this.state.addTicker])}, this.updateStocks);
    this.setState({addTicker: ""});
    //this.updateStocks();
  }

  handleTickerChange(event) {
    this.setState({addTicker: event.target.value});
  }

  updateStocks() {
    console.log("Updating Stocks");
    console.log(this.state.stocks);
    const requestOptions = {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ mode: 'stocks', data: {stocks: this.state.stocks} })
    };
    fetch('/api', requestOptions)
      .then(response => response.json())
      .then(data => this.setState({ postId: data.id }));
  }

  render() {
    if (this.state.stocks){
      return (
        <div className="stock-container">
          <AddTicker
            value={this.state.addTicker}
            onChange={this.handleTickerChange}
            onClick={this.handleAdd}
          />
          <ul>
            {
              this.state.stocks.map((elm) => {
                return (
                <li key={elm}>
                  {elm}
                  <button className="rem-btn" key={elm + " btn"} onClick={() => this.onRemove(elm)}>Remove</button>
                </li>);
              })
            }
          </ul>
        </div>
      );
    } else {
      return (
        <div className="stock-container">
          <p>Loading...</p>
        </div>
      );
    }
  }
}

function App() {
  // const [data, setData] = React.useState(0)

  // React.useEffect(() => {
  //   fetch("/api")
  //     .then((resp) => resp.json())
  //     .then((data) => setData(data.data.stocks[0]));
  // })

  return (
    <div className="App">
      <StocksManager />
    </div>
  );
}

export default App;
