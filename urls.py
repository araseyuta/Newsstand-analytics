from django.conf.urls.defaults import *

urlpatterns = patterns('',
    (r'^sales','app.views.sales'),
    (r'^app','app.views.app'),
    (r'^totalsales','app.views.totalsales'),
    (r'^register','app.views.register'),
    (r'^','app.views.index'),
#    (r'^make(.*)','latlng.views.latlng'),
#    (r'^books/book/(\d*)','bulk.views.opentime'),
    # Example:
    # (r'^foo/', include('foo.urls')),

    # Uncomment this for admin:
#     (r'^admin/', include('django.contrib.admin.urls')),
)
