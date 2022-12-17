import React, { Component } from 'react';
import SectionHeading from "./SectionHeading";
import { getLineOptions } from "./utils/dataPlot"
import Highcharts from 'highcharts'
import HighchartsReact from "highcharts-react-official";
import DataTableComponent from "./TablePagination";

class PopupWindow extends Component {

  show_list = (list, n_item_each_line) => {
    return list.map((item, idx) =>
        (idx+1) % n_item_each_line ? item + "   " : item + "\n"
    )
  }

  render_cards = (names) => {
    return names.map((name) =>
      <div key={name} className="cardSS">
        <h4 className="cardtitle"><b>{name}</b></h4>
        <p className="cardcontent">{
          typeof(this.props.summary[name]) == "number"
              ? this.props.summary[name] + "%"
              : typeof(this.props.summary[name]["date"]) != "undefined"
                ? this.props.summary[name]["profit"] + "% ( " + this.props.summary[name]["date"] + " )"
                : this.props.summary[name]["profit"] + "% ( " + this.props.summary[name]["year"] + "year )"
        }</p>
      </div>
    )
  }

  render() {
    let tb_item = ["season", "month", "week", "day", "total", "max", "min"]
    return(
        <div className="portfolio-modal modal fade" id={"portfolioModal" + this.props.ith} tabIndex="-1" role="dialog"
             aria-labelledby="portfolioModal1Label" aria-hidden="true">
          <div className="modal-dialog modal-xl" role="document">
            <div className="modal-content">
              <button className="close" type="button" data-dismiss="modal" aria-label="Close">
                <span aria-hidden="true"><i className="fas fa-times"/></span>
              </button>
              <div className="modal-body text-center">
                <div className="container">
                  <div className="row justify-content-center">
                    <div className="col-lg-12">
                      <SectionHeading title={"Details"}/>
                      {/*Portfolio Modal - Image*/}
                      <figure className="highcharts-figure">
                        {/*<div id={"area-container" + this.props.ith}*/}
                        {/*     style={{minWidth: "400px", height: "500px", width: "1000px", margin: "0 auto",}}>*/}
                        {/*</div>*/}
                        <HighchartsReact highcharts={Highcharts} options={getLineOptions(this.props.summary)}/>
                        <div>{this.render_cards(tb_item.slice(0, 4))}</div>
                        <div>{this.render_cards(tb_item.slice(4))}</div>
                        <p className="highcharts-description" style={{marginTop: "40px"}}>{this.props.signal.date + " "}
                          的隔日買入推薦:<br/><span className="signal" style={{whiteSpace: "pre"}}>{this.show_list(this.props.signal.buy, 5)}</span><br/>
                        </p>
                        <p className="highcharts-description" style={{marginTop: "25px"}}>{this.props.signal.date + " "}
                          的隔日賣出推薦:<br/><span className="signal" style={{whiteSpace: "pre"}}>{this.show_list(this.props.signal.sell, 5)}</span>
                        </p>
                      </figure>
                      <DataTableComponent data={this.props.records}/>
                      {/*Portfolio Modal - Text*/}
                      <button className="btn btn-primary" data-dismiss="modal"><i className="fas fa-times fa-fw"/>Close
                        Window
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
    )
  }
}

export default PopupWindow
