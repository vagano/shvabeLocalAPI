(function ($) {
    $.fn.imageWidget = function (options) {

         var settings = $.extend({
            // These are the defaults.
            backgroundColor: "#000000"
        }, options);

        this.css('background-color', settings.backgroundColor);
        this.css('background-image', 'url('+settings.imageSrc+')');
        return this;

    }
}(jQuery));
