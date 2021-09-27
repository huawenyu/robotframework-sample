from NetmikoOperator import NetmikoOperator

hoge = NetmikoOperator()

# Login to router
hoge.open_session('192.168.1.34','test','test','cisco_xr','xrv1')

# Check if state : Initial check
out = hoge.check_if_state('Gi0/0/0/0','xrv1')
if out is True:
    print('PASS!')

# Shutdown Interface
hoge.shutdown_interface('Gi0/0/0/0','shutdown-interface','xrv1')

# Check if state : after shutdown
out = hoge.check_if_state('Gi0/0/0/0','xrv1')
if out is False:
    print('PASS!')

# No Shutdown Interface
hoge.noshutdown_interface('Gi0/0/0/0','shutdown-interface','xrv1')

# Check if state : after no shutdown
out = hoge.check_if_state('Gi0/0/0/0','xrv1')
if out is True:
    print('PASS!')

# Logout from router
hoge.close_session('xrv1')
