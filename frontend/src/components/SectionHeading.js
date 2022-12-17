import React, { Component } from 'react';

class SectionHeading extends Component {
  render() {
    return (
      <div>
        <h2 className="page-section-heading text-center text-secondary mb-0">{this.props.title}</h2>
        <div className="divider-custom">
          <div className="divider-custom-line"/>
          <div className="divider-custom-icon"><i className="fas fa-star"/></div>
          <div className="divider-custom-line"/>
        </div>
      </div>
    )
  }
}

export default SectionHeading