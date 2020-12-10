function buildgraph(username, username_concat, container) {
    const timezone = new Date().getTimezoneOffset()
    var chart;
    var url = '/data/' + username + ':' + username_concat
    console.log(url)
    function requestData()
    {
        // Ajax call to get the Data from Flask
        //var url = '/data/' + username
        console.log(url)
        var requests = $.get(url);
        var tm = requests.done(function (result)
        {
            chart.series[0].setData(result, true)
            setTimeout(requestData, 50000);
        });
    }

    $(document).ready(function() {
        Highcharts.setOptions({
            global: {
                timezoneOffset: timezone
            },
            lang: {
                loading: 'Загрузка...',
                months: ['Января', 'Февраля', 'Марта', 'Апреля', 'Мая', 'Июня', 'Июля', 'Августа', 'Сентября', 'Октября', 'Ноября', 'Декабря'],
                weekdays: ['Воскресенье', 'Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница', 'Суббота'],
                shortWeekdays: ['вс', 'пн', 'вт', 'ср', 'чт', 'пт', 'сб'],
                week: 'Неделя',
                shortMonths: ['Янв.', 'Фев.', 'Мар.', 'Апр.', 'Май', 'Июн.', 'Июл.', 'Авг.', 'Сент.', 'Окт.', 'Нояб.', 'Дек.'],
                exportButtonTitle: "Экспорт",
                printButtonTitle: "Печать",
                rangeSelectorFrom: "С",
                rangeSelectorTo: "По",
                rangeSelectorZoom: "Период",
                downloadPNG: 'Загрузить в PNG',
                downloadJPEG: 'Загрузить в JPEG',
                downloadPDF: 'Загрузить в PDF',
                downloadSVG: 'Загрузить в SVG'
            }
        });
        chart = Highcharts.ganttChart(container, {

            chart: {
                renderTo: 'data-container',
                defaultSeriesType: 'spline',
                events: {
                    load: requestData
                }
            },

            title: {
                text: 'Мониторинг активности ' + username + ' в Telegram'
            },

            xAxis: [{
            }, {
                dateTimeLabelFormats: {
                    week: 'Неделя %W'
                }
            }],

            yAxis: {
                uniqueNames: true
            },

            navigator: {
                enabled: true,
                liveRedraw: true,
                series: {
                    type: 'gantt',
                    pointPlacement: 0.5,
                    pointPadding: 0.25
                },
                yAxis: {
                    min: 0,
                    max: 2,
                    reversed: true,
                    categories: []
                }
            },
            scrollbar: {
                enabled: true
            },
            rangeSelector: {
                buttons: [
                    {
                        count: 30,
                        type: 'minute',
                        text: '30м'
                    },
                    {
                        count: 1,
                        type: 'hour',
                        text: '1ч'
                    }, 
                    {
                        count: 6,
                        type: 'hour',
                        text: '6ч'
                    }, 
                    {
                        count: 1,
                        type: 'day',
                        text: '1д'
                    }, 
                    {
                        count: 1,
                        type: 'week',
                        text: '1н'
                    }, 
                    {
                        count: 1,
                        type: 'month',
                        text: '1М'
                    }, 
                    {
                        count: 6,
                        type: 'month',
                        text: '6М'
                    }, 
                    {
                        type: 'all',
                        text: 'Все'
                    }
                ],
                enabled: true,
                selected: 0
            },

            series: [{
                name: 'Статус',
                data: [
                    {
                        status : 1606603171000,
                        end : 1606603176000,
                        name : 'Offline'
                    }
                ]
            }],
        });
        
    });
}