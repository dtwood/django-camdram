function pad(n, width, z) {
  z = z || '0';
  n = n + '';
  return n.length >= width ? n : new Array(width - n.length + 1).join(z) + n;
}

var Diary = function(options) {
    this.diary = $('div#diary');
    this.url = options.url || "/diary_week";
    this.infinite_scroll_lock = false;
}

Diary.prototype.initialize = function() {
    var self = this;
    $('#load').click(function(e) {
	diary_start.subtract('days', 7);
	e.preventDefault();
	var week = diary_start.format('YYYY-MM-DD')
	$.ajax({url: self.url,
		data: {'week': week},
		success: function(data) {
		   self.diary.prepend(data.html);
		    }});
	window.history.replaceState('','','/diary/' + week + '?end=' + moment(diary_end).format('YYYY-MM-DD'));
	return false;
    });
    $(window).scroll(function() {
	if (!self.infinite_scroll_lock) {
	if( $(window).scrollTop() >= $(document).height() - $(window).height() - 50 ) {
	    self.infinite_scroll_lock = true;
	    diary_end.add('days', 7)
	    $.ajax({url: self.url,
		    data: {'week': diary_end.format('YYYY-MM-DD')},
		    success: function(data) {
			self.diary.append(data.html);
			self.infinite_scroll_lock = false;
			}});
	    
	    window.history.replaceState('','','/diary/' + diary_start.format('YYYY-MM-DD') + '?end=' + diary_end.format('YYYY-MM-DD'));
	}}});
	    
}
