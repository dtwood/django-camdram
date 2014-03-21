var Autocomplete = function(options) {
    this.form_selector = options.form_selector
    this.url = options.url || '/search/autocomplete'
    this.delay = parseInt(options.delay || 300)
    this.minimum_length = parseInt(options.minimum_length || 3)
    this.form_elem = null
    this.query_box = null
    this.cache = {}
    this.timeout
}

Autocomplete.prototype.setup = function() {
    var self = this;
    this.form_elem = $(this.form_selector);
    this.query_box = this.form_elem.find('#searchfield');
    
    // Watch the input box.
    this.query_box.focus(function(e) {
        self.suggest(this);
    }).blur(function(e) {
        window.setTimeout(function() {
            self.drawControl(false);
        }, 100)
    }).keyup(function(e) {
        e.preventDefault();
        if(e.keyCode == 38 || e.keyCode == 40)
            self.shiftOption(this, (e.keyCode == 40));
        else if(e.keyCode == 13)
            self.chooseOption(this);
        else if(e.keyCode != 37 && e.keyCode != 39)
            self.suggest(this);
        return false;
    }).keypress(function(e) {
        if(e.keyCode == 13)
        {
            e.preventDefault();
            return false;
        }
        return true;
    }).on('paste', function() {
            self.suggest(this);
    });


    this.form_elem.find('.results ul li').mousemove(function() {
	console.log(hello);
        if (!$(this).hasClass('active')) {
            self.form_elem.find(".results ul li").removeClass('active');
            $(this).addClass('active');
        }
    });
    
    this.form_elem.find('.fulltext a').click(function(e) {
        e.preventDefault();
        $('#search_form').submit();
    });
}

Autocomplete.prototype.suggest = function(field) {
    if (this.timeout > 0) {
        window.clearTimeout(this.timeout);
    }
    var self = this
    this.timeout = window.setTimeout(function () {self.requestOptions()}, 100);
}

Autocomplete.prototype.requestOptions = function() {
    var self = this
    if (this.change_count > 0) {
        return;
    }
    var query = this.query_box.val();
    if(query.length < 2) {
        this.drawControl(false);
        return;
    }

//    if (typeof this.cache[query] != 'undefined') {
//        //We've done this request before, so load the results from the cache
//        this.displayResults(query, this.cache[query])
//    }
//    else {
        this.form_elem.find(".fa-spinner").fadeIn(100);
        // Activate the field
	$.ajax({url: self.url,
	    data: {'q': query},
	    success: function(data) {
		self.displayResults(data, query)
//		self.cache[query] = data;
		self.form_elem.find(".fa-spinner").fadeOut(100);
            }
	   });
//    }
}

Autocomplete.prototype.shiftOption = function(field, down) {
    // Find currently active item
    var $results = this.form_elem.find(".results ul li");
    if($results.length == 0) return;
    // Find currently selected one
    var current = $results.filter('.active');
    current.removeClass('active');

    if (down && current.length == 0) {
        $results.first().addClass('active');
    }
    else if (down && current.next().length > 0) {
        current.next().addClass('active');
    }
    else if (!down && current.prev().length > 0) {
        current.prev().addClass('active');
    }
}

Autocomplete.prototype.chooseOption = function(e) {
    // If we do have a selected item then jump to it, otherwise just search
    var $active_item = this.form_elem.find(".results ul li.active");
    if($active_item.length == 0) {
        this.form_elem.submit();
    }
    else {
        this.form_elem.val($active_item.find('span').text());
        this.drawControl(false);
        window.location.href = $active_item.children('a').attr('href');
    }
}

Autocomplete.prototype.drawControl = function(show) {
    $results = this.form_elem.find(".results");

    if(show) {
        $results.show().stop();
        var previous_height = $results.height();
        $results.css('height', 'auto');
        var height =  $results.height();

        $results.css('height', previous_height).animate({"height": height + "px", "opacity": 1.0}, 200);
    }
    else $results.animate({'opacity' : 0.0, 'height' : '0px'}, 200, function() { $(this).css({'display': 'none'})});
}

Autocomplete.prototype.displayResults = function(items, query) {
    var self = this
    this.form_elem.find(".results ul li:not(.fulltext)").remove();
    if (items.length > 0) {
        this.form_elem.find(".noresults").hide();
        for (var i = 0; i < items.length; i++) {
            var result = items[i];
            var item = $("<li/>").mouseenter(function() {
		    if (!$(this).hasClass('active')) {
			self.form_elem.find(".results ul li").removeClass('active');
		    }
		    $(this).addClass('active');
		});
	    
            // Add in the text
            var link = $("<a/>")
                .attr('href', result.link)
                .addClass('resultText')
                .appendTo(item)
                .click(function(e) {
                    e.preventDefault();
                    self.chooseOption(e);
                });
	    
            // Add in the icon
            switch (result.type) {
            case 'show' : var icon_class = "fa fa-ticket"; break;
            case 'venue' : var icon_class = "fa fa-home"; break;
            case 'society' : var icon_class = "fa fa-briefcase"; break;
            default: var icon_class = 'fa fa-user';
            }
            $("<i/>").addClass(icon_class).appendTo(link);
	    
            $('<span/>').text(result.name + " " + result.string).appendTo(link);
	    
            // Add item into the page
            this.form_elem.find(".results ul").append(item);
        }
        this.drawControl(true, (items.length * 40));
    } else {
        this.form_elem.find(".noresults").show();
        this.form_elem.find('.noresults .query').text(query);
        this.drawControl(true);
    }
    this.form_elem.find('.query').text(query);
}



$(document).ready(function() {
    window.autocomplete = new Autocomplete({
        form_selector: '#search_form'
    })
    window.autocomplete.setup()
})
