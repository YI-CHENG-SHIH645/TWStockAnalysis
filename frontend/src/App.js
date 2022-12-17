import React, { Component } from 'react';
import GridItem from "./components/GridItem";
import PopupWindow from "./components/PopupWindow";
import SectionHeading from "./components/SectionHeading";
import './App.css';


const base_url = '35.234.8.96:3000'

class App extends Component{
  state = {}

  componentDidMount() {
    fetch(`http://${base_url}/info.json`)
        .then(response => response.json())
        .then(data => this.setState({"latest_signal": data['latest_signal']}))
    fetch(`http://${base_url}/info.json`)
        .then(response => response.json())
        .then(data => this.setState({"strategies_summary": data['strategies_summary']}))
    fetch(`http://${base_url}/info.json`)
        .then(response => response.json())
        .then(data => {
            this.setState({"trading_record": data['trading_record']});
        })
  }

  renderItems = (summaries) => {
    return summaries.map((item, idx) =>
      <GridItem key={idx} summary={item} ith={idx+1}/>
    )
  }

  renderWindows = (summaries, signal, records) => {
    return summaries.map((item, idx) =>
      <PopupWindow key={idx} summary={item} signal={signal[idx]} records={records[idx].records} ith={idx+1}/>
    )
  }

  render() {
    return (
        <div>
          <section className="page-section portfolio" id="portfolio">
            <div className="container">
              <SectionHeading title={"策略回測"}/>
              <div className="row">
              {this.state.strategies_summary && this.renderItems(this.state.strategies_summary)}
              </div>
            </div>
          </section>
          {this.state.latest_signal && this.state.strategies_summary && this.state.trading_record
          && this.renderWindows(this.state.strategies_summary, this.state.latest_signal, this.state.trading_record)}
        </div>
    )
  }
}

export default App;
export { base_url };
