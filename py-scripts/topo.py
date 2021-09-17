test_1_1 = {
    'client_number': 1,
    'server_number': 1,
    'router_number': 0,
    'server_thread': 1,
    'client_thread': 1,
    'bw': {
        'client_server': [
            [5,5,5,5,5],
            [5,5,5,5,5],
            [5,5,5,5,5],
            [5,5,5,5,5],
            [5,5,5,5,5]
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

Middleware_client_server = {
    'client_number': 5,
    'server_number': 5,
    'router_number': 0,
    'server_thread': 10,
    'client_thread': 10,
    'bw': {
        'client_server': [
            [5,5,5,5,5],
            [5,5,5,5,5],
            [5,5,5,5,5],
            [5,5,5,5,5],
            [5,5,5,5,5]
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
        'client': .4,
        'server': .4,
        'router': 0,
    }
}