from olpcproxy import dispatch

def make_app(global_conf, data_dir):
    return dispatch.Dispatcher(data_dir)

