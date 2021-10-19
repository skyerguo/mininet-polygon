test_1_1 = {
    'client_number': 1,
    'server_number': 1,
    'router_number': 0,
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
        'router': 0.0,
    }
}

test_1_1_1 = {
    'client_number': 1,
    'server_number': 1,
    'router_number': 1,
    'server_thread': 1,
    'client_thread': 1,
    'router_thread': 1,
    'bw': {
        'client_server': [
            [50,50],
            [50,50]
        ],
        'client_router': [
            [50,50],
            [50,50]
        ],
        'router_server': [
            [1000,50],
            [50,1000]
        ],
        'router_router': [
            [50,50],
            [50,50]
        ]
    },
    'delay': {
        'client_server': [
            [10,30],
            [15,20]
        ],
        'client_router': [
            [10,30],
            [15,20]
        ],
        'router_server': [
            [1,30],
            [15,1]
        ],
        'router_router': [
            [0,30],
            [15,0]
        ],
    },
    'cpu': {
        'client': .2,
        'server': .3,
        'router': .2,
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
    'router_number': 0,
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
        'router': 0,
    }
}


Middleware_client_router_server = {
    'client_number': 2,
    'server_number': 2,
    'router_number': 2,
    'server_thread': 1,
    'client_thread': 1,
    'router_thread': 1,
    'bw': {
        'client_server': [
            [50,50],
            [50,50]
        ],
        'client_router': [
            [50,50],
            [50,50]
        ],
        'router_server': [
            [1000,50],
            [50,1000]
        ],
        'router_router': [
            [50,50],
            [50,50]
        ]
    },
    'delay': {
        'client_server': [
            [10,30],
            [15,20]
        ],
        'client_router': [
            [10,30],
            [15,20]
        ],
        'router_server': [
            [1,30],
            [15,1]
        ],
        'router_router': [
            [0,30],
            [15,0]
        ],
    },
    'cpu': {
        'client': .2,
        'server': .3,
        'router': .2,
    },
    'zone': {
        'as',
        'na',
        'eu',
    }
}