function pad(n, width, z) {
  z = z || '0';
  n = n + '';
  return n.length >= width ? n : new Array(width - n.length + 1).join(z) + n;
}

var Diary = function(options) {
    this.diary = $('div#diary');
    this.url = options.url || "/diary_week";
    this.infinite_scroll_lock = false;
    this.prev_lock = false;
}

Diary.prototype.initialize = function() {
    var self = this;
    $('#load_previous').click(function(e) {
	e.preventDefault();
	if (!self.prevlock) {
	    self.prev_lock = true;
	    diary_start.subtract('days', 7);
	    var week = diary_start.format('YYYY-MM-DD')
	    $.ajax({url: self.url,
		    data: {'week': week},
		    success: function(data) {
			start_label = self.diary.find('h4').first();
			if (data.term_label && start_label.html() == data.term_label) {
			    $(data.html).insertAfter(start_label);
			} else {
			    label = $("<h4></h4>").html(data.term_label);
			    self.diary.prepend(data.html);
			    self.diary.prepend(label);
			}
			self.prev_lock = false;
		    },
		    error: function() {
			diary_start.add('days', 7)
			self.prev_lock = false;
		    }
		   });
	    window.history.replaceState('','','/diary/' + week + '?end=' + moment(diary_end).format('YYYY-MM-DD'));
	}
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
			end_label = self.diary.find("h4").last();
			if (!data.term_label || end_label.html() == data.term_label) {
			    self.diary.append(data.html);
			} else {
			    label = $("<h4></h4>").html(data.term_label);
			    self.diary.append(label);
			    self.diary.append(data.html);
			}
			self.infinite_scroll_lock = false;
		    },
		    error: function() {
			diary_end.subtract('days', 7);
			self.infinite_scroll_lock = false;
		    }
		   });
	    
	    window.history.replaceState('','','/diary/' + diary_start.format('YYYY-MM-DD') + '?end=' + diary_end.format('YYYY-MM-DD'));
	}}});
	    
}
