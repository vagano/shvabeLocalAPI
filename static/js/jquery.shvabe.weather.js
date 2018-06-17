(function ($) {
    $.fn.weather = function (options) {

        var settings = $.extend({
            apiUrl: "http://localhost:5000/api/get_current_temp",
            updateFreq: 300000,
            authToken: ""
        }, options);

        setInterval(doUpdate, settings.updateFreq, this);

        function doUpdate(container) {

            var temp = 0;

            $.ajax({
                async: true,
                url: settings.apiUrl,
                dataType: "json",
                success: function (data) {
                    temp = data.temperature;
                    var tempString = temp + '°C';

                    if (temp > 0) {
                        tempString = '+' + tempString;
                    }

                    container.html('<span>' + tempString + '</span>');
                }
            });
        }

        doUpdate(this);

        return this;

    }
}(jQuery));