document.addEventListener('DOMContentLoaded', function () {
    // 데이터를 가져와서 차트를 업데이트하는 함수
    fetchAndUpdateData().then(data => {
        // 차트 생성
        Highcharts.chart('container2', {
            chart: {
                type: 'column'
            },
            title: {
                align: 'center',
                text: '형량 통계'
            },
            accessibility: {
                announceNewData: {
                    enabled: true
                }
            },
            xAxis: {
                type: 'category',
                accessibility: {
                    rangeDescription: 'Range: 2010 to 2020'
                }
                
            },
            yAxis: {
                title: {
                    text: '사건수'
                }
            },
            legend: {
                enabled: false
            },
            plotOptions: {
                series: {
                    borderWidth: 0,
                    dataLabels: {
                        enabled: true,
                        format: '{point.y}'
                    }
                }
            },
            tooltip: {
                headerFormat: '<span style="font-size:11px">{series.name}</span><br>',
                pointFormat: '<span style="color:{point.color}">{point.name}</span>: <b>{point.y}</b> of total<br/>'
            },
            series: [
                {
                    name: 'Categories',
                    colorByPoint: true,
                    data: [
                        {
                            name: '징역',
                            y: data.jailcount,
                            drilldown: '징역'
                        },
                        {
                            name: '집행유예',
                            y: data.probationcount,
                            drilldown: '집행유예'
                        },
                        {
                            name: '벌금',
                            y: data.finecount,
                            drilldown: '벌금'
                        }
                    ]
                }
            ],
            drilldown: {
                breadcrumbs: {
                    position: {
                        align: 'right'
                    }
                },
                series: [
                    {
                        name: '징역',
                        id: '징역',
                        data: data.drilldown.series[0].data
                            
                        
                    },
                    {
                        name: '집행유예',
                        id: '집행유예',
                        data:data.drilldown.series[1].data
                    },
                    {
                        name: '벌금',
                        id: '벌금',
                        data: data.drilldown.series[2].data
                    }
                ]
            },
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
        });
    });
});