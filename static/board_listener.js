// Some useful globals
var human_turn = true; 
var movetime = 200;
var THINKTIME = 2000;
var moves_left = 0;

// Add listeners
$(document).ready(function() {
    $('div.cup').click(function() {
        var id = $(this).attr('id');
        //alert("I hear you");
        make_move(id);
    });

    $('div.goal').click(function() {
        var id = $(this).attr('id');
        var beans = 1;
        update_goal(id,beans);
    });
});

function update_cups(id, beans) {
    var cup = $('#' + id);
    cup.empty();
    beans = parseInt(beans);

    if (beans <= 6) {
        cup.append("<img src='/static/img/beans/"+beans+".png'>");
    } else {
        cup.append("<img src='/static/img/beans/lots.png'>");
        cup.append("<div class='cupnum'>"+beans+"</div>")
    }

    cup.attr('beans', beans);
};

function update_goal(id, new_beans) {
    var goal = $('#'+id);
    new_beans = parseInt(new_beans);
    
    goal.empty();
    goal.attr('beans', new_beans);

    if (new_beans <= 9) {
        goal.append("<img src='/static/img/goals/"+new_beans+".png'>");
    } else {
        goal.append("<img src='/static/img/goals/lots.png'>");
        goal.append("<div class=goalnum>" + new_beans + "</div>");
    }
}

function update_difficulty(dif) {
    $('#difficulty_num').text(dif);
}

function update_speed(sp) { 
    var times = [1500,1000,500,250,100,50,0];
    sp = parseInt(sp);
    movetime = times[sp-1];
}

function get_beans(id) {
    return parseInt(
        $('#'+id).attr('beans')
    );
}

function top_row() { 
    var ids = new Array(6);
    for (let i=1; i<7; i++) {
        ids[i-1] = 'cup1'+i;
    }
    return ids 
}

function bottom_row() { 
    // Note: in the code the bottom row is 
    // indexed backwards
    var ids = new Array(6);
    for (let i=6; i>0; i--) {
        ids[6-i] = 'cup2'+i;
    }
    return ids;
}

/* 
    Build a json object representing the board that can be
    sent to python for processing
*/

function get_state() {
    var top_ids = top_row();
    var bottom_ids = bottom_row();

    // Get row data 
    var top = new Array(6);
    var bottom = new Array(6);
    for (let i=0; i<6; i++){
        top[i] = get_beans(top_ids[i]);
        bottom[i] = get_beans(bottom_ids[i]);
    }

    // Everything else is a simple jQuery call 
    return {
        'top': top, 
        'bottom': bottom, 
        'p1_turn': human_turn,
        'p1_score': $('#p1_goal').attr('beans'),
        'p2_score': $('#p2_goal').attr('beans')
    }
}

function make_move(id) { 
    // I guess this could cause a deadlock if you clicked a cup
    // twice in two nanoseconds, but.. eh
    if (moves_left) { return; }

    var state = get_state();
    var cid = 'cid'; 
    state[cid] = id; 

    fetch('/move', {
        headers: {
            'content-type': 'application/json'
        }, 
        method: 'POST',
        body: JSON.stringify(state)
    }).then(function tojs(p) {
        p.json().then( 
            function proc(resp) { process_move(resp); }
        )
    });
}

function animate_move(resp, delay) { 
    var moves = resp['moves'];
    moves_left += resp['n_updates'];

    for (let i=0; i<resp['n_updates']; i++) {
        if (moves[i]['state'] == 'gameover') { 
            setTimeout(
                function () {
                    moves_left = 0;
                    return gameover(moves[i]); 
                }, (movetime*i) + delay
            )
            continue
        }

        setTimeout(function fn(){
            if (moves[i]['id'][0] == 'c') {
                update_cups(moves[i]['id'], moves[i]['beans']);
            } else { 
                update_goal(moves[i]['id'], moves[i]['beans']);
            }
            moves_left -= 1;
        }, (movetime*i)+delay); 
    }
}

function process_move(resp) {
    /*
        Move schema: 
            state: one of {'invalid', 'valid'},
            n_updates: len of update list
            updates: [
                {
                    state: {'valid', 'gameover'},
                    beans: num 
                    id: id of cup/goal entity to update
                }
            ],
            board: the boardstate object it results in

    */
    if (resp['state'] != 'valid') { return; }
    animate_move(resp,0);

    // While we're waiting on the animation, get the AI's response
    var req = {
        'depth': $('#difficulty_num').text(),
        'state': resp['board']
    }

    var human_moves = resp['n_updates'];

    // Animate the computer
    var comp = $('#computer');
    
    var elapsed = human_moves*movetime;
    setTimeout(() => {
        comp.empty();
        comp.append('<img src="/static/img/adversary/thinking.png"/>')
    }, elapsed);

    
    // Get computer response and animate it
    var fetch_time = new Date().getTime();
    f = fetch(
        '/bot', {
            headers: {
                'content-type': 'application/json'
            }, 
            method: 'POST',
            body: JSON.stringify(req)
        }
    ).then(function tojs(resp_ai) {
        resp_ai.json().then(
            function fn(resp_ai) { 
                // If AI was actually thinking, don't wait to set his face to 
                // be solving when we get here
                var time_to_solve = (new Date()).getTime() - fetch_time;
                var time_remaining = elapsed+THINKTIME;

                console.log(time_to_solve);
                console.log(time_remaining);

                var delay; 
                if (time_remaining - time_to_solve > 0) { 
                    delay = time_remaining-time_to_solve; 
                }
                else {
                    delay = 0;
                }
                setTimeout(() => {
                    comp.empty();
                    comp.append('<img src="/static/img/adversary/solving.png"/>')
                }, delay); 

                // Update after done thinking (if applicable) and moving
                animate_move(resp_ai, delay);
                setTimeout(() => {
                    comp.empty();
                    comp.append('<img src="/static/img/adversary/waiting.png"/>')
                }, delay+resp_ai['n_updates']*movetime);
            }
        )
    })
}

function gameover(resp) { 
    var comp = $('#computer');

    // Keep him smug if he wins
    if (resp['winner'] == 2) {
        alert(
            ' =========== Game Over ========== \n' +
            ' .....Better luck next time......\n' +
            ' ...........The bot wins......... '
        );
        reset();

    } else {
        // Otherwise make him normal again 
        comp.empty();
        comp.append('<img src="/static/img/adversary/waiting.png"/>');

        // Delay it bc it takes a sec for the picture to change
        setTimeout(() => {
            if (resp['winner'] == 1) {
                alert(
                    ' =========== Game Over ========== \n' +
                    ' ........Congradulations!........\n' +
                    ' ........You beat the bot!....... '
                );
            } else {
                alert(
                    ' =========== Game Over ========== \n' +
                    ' ........Not bad, not bad........\n' +
                    " ...........It's a tie!.......... "
                );
            } 
            reset(); 
        }, 100);
    }
    
}

function reset() {
    $(".cup").each(function() {
        update_cups(this.id, 4);
    });
    $(".goal").each(function() {
        update_goal(this.id, 0);
    });

    moves_left=0;
    comp.empty();
    comp.append('<img src="/static/img/adversary/waiting.png"/>');
}