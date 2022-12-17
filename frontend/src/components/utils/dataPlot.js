export const getLineOptions = (data) => {
  return {

    title: {
      text: data.strategy_name
    },

    xAxis: {
        type: "datetime"
    },

    yAxis: {
      title: {
        text: 'cumulative return'
      }
    },

    series: [
      {
        name: data.strategy_name,
        data: Object.entries(data.daily_return).map(([k, v]) => [new Date(k), v])
      }
    ],

    responsive: {
      rules: [{
        condition: {
          maxWidth: 500
        },
        chartOptions: {
          legend: {
            layout: 'horizontal',
            align: 'center',
            verticalAlign: 'bottom'
          }
        }
      }]
    }

  }
}
