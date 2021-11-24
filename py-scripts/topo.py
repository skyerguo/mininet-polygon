test_1_1 = {
    'client_number': 1,
    'server_number': 1,
    'dispatcher_number': 0,
    'server_thread': 1,
    'client_thread': 1,
    'bw': {
        'client_server': [
            [50,50,50,50,50],
            [50,50,50,50,50],
            [50,50,50,50,50],
            [50,50,50,50,50],
            [50,50,50,50,50]
        ],
    },
    'delay': {
        'client_server': [
            [10,20,40,100,150],
            [15,25,30,80,100],
            [100,120,50,20,70],
            [50,40,10,60,100],
            [150,130,70,50,10]
        ],
    },
    'cpu': {
        'client': 0.2,
        'server': 0.5,
        'dispatcher': 0.0,
    }
}

test_1_1_1 = {
    'client_number': 1,
    'server_number': 1,
    'dispatcher_number': 1,
    'server_thread': 1,
    'client_thread': 1,
    'dispatcher_thread': 1,
    'bw': {
        'client_server': [
            [50,50],
            [50,50]
        ],
        'client_dispatcher': [
            [50,50],
            [50,50]
        ],
        'dispatcher_server': [
            [1000,50],
            [50,1000]
        ],
        'dispatcher_dispatcher': [
            [50,50],
            [50,50]
        ]
    },
    'delay': {
        'client_server': [
            [10,30],
            [15,20]
        ],
        'client_dispatcher': [
            [10,30],
            [15,20]
        ],
        'dispatcher_server': [
            [1,30],
            [15,1]
        ],
        'dispatcher_dispatcher': [
            [0,30],
            [15,0]
        ],
    },
    'cpu': {
        'client': .2,
        'server': .3,
        'dispatcher': .2,
    },
    'zone': {
        'as',
        'na',
        'eu',
    }
}

Middleware_client_server = {
    'client_number': 10,
    'server_number': 10,
    'dispatcher_number': 0,
    'server_thread': 3,
    'client_thread': 3,
    'bw': {
        'client_server': [
            [50,50,50,50,50,50,50,50,50,50],
            [50,50,50,50,50,50,50,50,50,50],
            [50,50,50,50,50,50,50,50,50,50],
            [50,50,50,50,50,50,50,50,50,50],
            [50,50,50,50,50,50,50,50,50,50],
            [50,50,50,50,50,50,50,50,50,50],
            [50,50,50,50,50,50,50,50,50,50],
            [50,50,50,50,50,50,50,50,50,50],
            [50,50,50,50,50,50,50,50,50,50],
            [50,50,50,50,50,50,50,50,50,50]
        ],
    },
    'delay': {
        'client_server': [
            [10,20,40,100,150,10,20,40,100,150],
            [15,25,30,80,100,15,25,30,80,100,],
            [100,120,50,20,70,100,120,50,20,70],
            [50,40,10,60,100,50,40,10,60,100],
            [150,130,70,50,10,150,130,70,50,10],
            [10,20,40,100,150,10,20,40,100,150],
            [15,25,30,80,100,15,25,30,80,100,],
            [100,120,50,20,70,100,120,50,20,70],
            [50,40,10,60,100,50,40,10,60,100],
            [150,130,70,50,10,150,130,70,50,10]
        ],
    },
    'cpu': {
        'client': .2,
        'server': .5,
        'dispatcher': 0,
    }
}


Middleware_client_dispatcher_server_test = {
    'client_number': 2,
    'server_number': 2,
    'dispatcher_number': 2,
    'server_thread': 1,
    'client_thread': 1,
    'dispatcher_thread': 1,
    'bw': {
        'client_server': [
            [5,2],
            [2,5]
        ],
        'client_dispatcher': [
            [5,2],
            [2,5]
        ],
        'dispatcher_server': [
            [10,3],
            [3,10]
        ],
    },
    'delay': {
        'client_server': [
            [30,300],
            [300,30]
        ],
        'client_dispatcher': [
            [20,100],
            [100,20]
        ],
        'dispatcher_server': [
            [3,100],
            [100,3]
        ],
    },
    'cpu': {
        'client': .2,
        'server': .4,
        'dispatcher': .3,
    },
    # 'zone': {
    #     'as',
    #     'na',
    # }
}

Middleware_client_dispatcher_server_main = {
    'client_number': 5,
    'server_number': 5,
    'dispatcher_number': 5,
    'server_thread': 5,
    'client_thread': 5,
    'dispatcher_thread': 5,
    'bw': {
        'client_server': [
            [5.00,2.07,1.98,1.89,3.15],
            [2.07,4.00,1.36,0.91,1.26],
            [1.98,1.36,4.00,0.83,1.14],
            [1.89,0.91,0.83,5.00,5.00],
            [3.15,0.26,1.14,5.00,5.00],
        ],
        'client_dispatcher': [
            [5,5,5,5,5],
            [5,5,5,5,5],
            [5,5,5,5,5],
            [5,5,5,5,5],
            [5,5,5,5,5],
        ],
        'dispatcher_server': [
            [5.00,2.07,1.98,1.89,3.15],
            [2.07,4.00,1.36,0.91,1.26],
            [1.98,1.36,4.00,0.83,1.14],
            [1.89,0.91,0.83,5.00,5.00],
            [3.15,0.26,1.14,5.00,5.00],
        ],
    },
    'delay': { # 这里的delay，实际上记录的是rtt的值
        'client_server': [
            [100,157,162,170,105],
            [157,150,224,317,240], 
            [162,224,150,330,261],
            [170,317,330,100,70],
            [105,240,261,70,100],
        ],
        'client_dispatcher': [
            [100*0.67,157*0.67,162*0.67,170*0.67,105*0.67],
            [157*0.67,150*0.67,224*0.67,317*0.67,240*0.67], 
            [162*0.67,224*0.67,150*0.67,330*0.67,261*0.67],
            [170*0.67,317*0.67,330*0.67,100*0.67,70*0.67],
            [105*0.67,240*0.67,261*0.67,70*0.67,100*0.67],
        ],
        'dispatcher_server': [
            [100*0.33,157*0.33,162*0.33,170*0.33,105*0.33],
            [157*0.33,150*0.33,224*0.33,317*0.33,240*0.33], 
            [162*0.33,224*0.33,150*0.33,330*0.33,261*0.33],
            [170*0.33,317*0.33,330*0.33,100*0.33,70*0.33],
            [105*0.33,240*0.33,261*0.33,70*0.33,100*0.33],
        ],
    },
    'cpu': {
        'client': .1,
        'server': .3,
        'dispatcher': .5,
    },
    # 'zone': {
    #     'as',
    #     'na',
    # }
}

