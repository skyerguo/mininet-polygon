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


Middleware_client_dispatcher_server = {
    'client_number': 2,
    'server_number': 2,
    'dispatcher_number': 2,
    'server_thread': 1,
    'client_thread': 1,
    'dispatcher_thread': 1,
    'bw': {
        'client_server': [
            [5,1],
            [1,5]
        ],
        'client_dispatcher': [
            [5,1],
            [1,5]
        ],
        'dispatcher_server': [
            [10,3],
            [3,10]
        ],
        'dispatcher_dispatcher': [
            [10,10],
            [10,10]
        ]
    },
    'delay': {
        'client_server': [
            [20,200],
            [200,20]
        ],
        'client_dispatcher': [
            [20,200],
            [200,20]
        ],
        'dispatcher_server': [
            [1,100],
            [100,1]
        ],
        'dispatcher_dispatcher': [
            [0.1,1],
            [1,0.1]
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

