import React, { Component } from 'react';
import { base_url } from "../App";

class GridItem extends Component {
  render() {
    return(
        <div className="col-md-6 col-lg-6 mb-5">
          <div className="portfolio-item mx-auto" data-toggle="modal" data-target={"#portfolioModal" + this.props.ith}>
            <div className="portfolio-item-caption d-flex align-items-center justify-content-center h-100 w-100">
              <div className="portfolio-item-caption-content text-center text-white">
                <i className="fas fa-plus fa-3x"/>
              </div>
            </div>
            <img className="img-fluid" src={`http://${base_url}/public/${this.props.summary.strategy_name}.png`} alt=""/>
            <div className="top-left">{this.props.summary.strategy_name}</div>
            <div className="left">年化報酬<br/>
              <span className="btdata">
                {this.props.summary['annual_return'] + "%"}
              </span>
            </div>
            <div className="middle">當前檔數<br/>
              <span className="btdata">
                {this.props.summary['holding']}
              </span>
            </div>
            <div className="right">最大跌幅<br/>
              <span className="btdata">
                {this.props.summary['mdd'] + "%"}
              </span>
            </div>
          </div>
        </div>
    )
  }
}

export default GridItem