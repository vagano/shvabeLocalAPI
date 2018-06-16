(function ($) {
    $.fn.analogClock = function () {

        this.html('<div class="hours-container">\n' +
            '        <div class="hours"></div>\n' +
            '    </div>\n' +
            '    <div class="minutes-container">\n' +
            '        <div class="minutes"></div>\n' +
            '    </div>\n' +
            '    <div class="seconds-container">\n' +
            '        <div class="seconds"></div>\n' +
            '    </div>');

        function initLocalClocks(wrapper) {
            var date = new Date;
            var seconds = date.getSeconds();
            var minutes = date.getMinutes();
            var hours = date.getHours();
            var hands = [{hand: 'hours', angle: (hours * 30) + (minutes / 2)}, {
                hand: 'minutes',
                angle: (minutes * 6)
            }, {hand: 'seconds', angle: (seconds * 6)}];
            for (var j = 0; j < hands.length; j++) {
                var elements = wrapper.find('.' + hands[j].hand);
                for (var k = 0; k < elements.length; k++) {
                    elements[k].style.webkitTransform = 'rotateZ(' + hands[j].angle + 'deg)';
                    elements[k].style.transform = 'rotateZ(' + hands[j].angle + 'deg)';
                    if (hands[j].hand === 'minutes') {
                        elements[k].parentNode.setAttribute('data-second-angle', hands[j + 1].angle);
                    }
                }
            }
        }

        function moveSecondHands(wrapper) {
            var containers = wrapper.find('.seconds-container');
            setInterval(function () {
                for (var i = 0; i < containers.length; i++) {
                    if (containers[i].angle === undefined) {
                        containers[i].angle = 6;
                    } else {
                        containers[i].angle += 6;
                    }
                    containers[i].style.webkitTransform = 'rotateZ(' + containers[i].angle + 'deg)';
                    containers[i].style.transform = 'rotateZ(' + containers[i].angle + 'deg)';
                }
            }, 1000);
            for (var i = 0; i < containers.length; i++) {
                var randomOffset = Math.floor(Math.random() * (100 - 10 + 1)) + 10;
                containers[i].style.webkitTransitionDelay = '0.0' + randomOffset + 's';
                containers[i].style.transitionDelay = '0.0' + randomOffset + 's';
            }
        }

        function setUpMinuteHands(wrapper) {
            var minutesContainers = wrapper.find('.minutes-container');
			var hourContainers = wrapper.find('.hours-container');
			var secondAngle = minutesContainers[0].getAttribute('data-second-angle');
			if (secondAngle > 0) {
				var delay = (((360 - secondAngle) / 6) + 0.1) * 10;
				setTimeout(function () {
					moveMinuteHands(minutesContainers);
					moveHourHands(hourContainers);
				}, delay);
			}
		}

        function moveMinuteHands(containers) {
            for (var i = 0; i < containers.length; i++) {
				containers[i].style.webkitTransform = 'rotateZ(6deg)';
				containers[i].style.transform = 'rotateZ(6deg)';
			}
			setInterval(function () {
				for (var i = 0; i < containers.length; i++) {
					if (containers[i].angle === undefined) {
						containers[i].angle = 12;
					} else {
						containers[i].angle += 6;
					}
					containers[i].style.webkitTransform = 'rotateZ(' + containers[i].angle + 'deg)';
					containers[i].style.transform = 'rotateZ(' + containers[i].angle + 'deg)';
				}
			}, 60000);
		}
		
		function moveHourHands(containers) {
			for (var i = 0; i < containers.length; i++) {
				containers[i].style.webkitTransform = 'rotateZ(0.5deg)';
				containers[i].style.transform = 'rotateZ(0.5deg)';
			}	
			setInterval(function () {
					for (var i = 0; i < containers.length; i++) {
						if (containers[i].angle === undefined) {
							containers[i].angle = 1;
					} else {
						containers[i].angle += 0.5;
					}
					containers[i].style.webkitTransform = 'rotateZ(' + containers[i].angle + 'deg)';
					containers[i].style.transform = 'rotateZ(' + containers[i].angle + 'deg)';
				}
			}, 60000);
		}

        initLocalClocks(this);
        moveSecondHands(this);
        setUpMinuteHands(this);

        return this;

    }
}(jQuery));

(function ($) {
    $.fn.digitalClock = function () {

        this.html('<span></span>');

        function startTime(wrapper) {
            var today = new Date();
            var h = today.getHours();
            var m = today.getMinutes();
            //h = checkTime(h);
            m = checkTime(m);
            wrapper.find("span").html(h + "<b class='blink_me'>:</b>" + m);
            var t = setTimeout(startTime, 500,wrapper);
        }

        function checkTime(i) {
            if (i < 10) {
                i = "0" + i
            }
            ;  // add zero in front of numbers < 10
            return i;
        }

        startTime(this);

        return this;

    }
}(jQuery));

