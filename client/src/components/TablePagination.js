import React from "react";
import DataTable from 'react-data-table-component';
import DataTableExtensions from 'react-data-table-component-extensions'
import "react-data-table-component-extensions/dist/index.css";


class DataTableComponent extends React.Component {
  col_to_show = ['sid', 'open_date', 'open_price',
    'long_short', 'shares', 'close_date', 'close_price', 'holding_days', 'pnl']
  columns = Object.keys(this.props.data[0]).map( (k) => {
    return {
      name: k,
      selector: k,
      sortable: true,
    }
  }).filter( (obj) => this.col_to_show.includes(obj['selector']))


  render() {
    return (
      <DataTableExtensions data={this.props.data} columns={this.columns} filterHidden={false}>
        <DataTable
          columns={this.columns}
          pagination={true}
          highlightOnHover={true}
          data={this.props.data}
        />
      </DataTableExtensions>
    )
  }
}

export default DataTableComponent
