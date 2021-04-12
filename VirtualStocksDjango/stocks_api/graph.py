import io
import base64
import seaborn as sns
import matplotlib.pyplot as plt
from io import StringIO
import numpy as np
from django.http import HttpResponse
from datetime import datetime as dt

# @api_view(['GET'])
# @authentication_classes([TokenAuthentication])
# @permission_classes([IsAuthenticated])
# def plot_graph():
#     plt.show()





def return_graph(data):
    sns.set()
    sns.set_theme(style="darkgrid")
    # x=['2021-04-08T09:55:34.246721Z', '2021-04-12T11:04:02.902895Z', '2021-04-12T11:10:12.840286Z', '2021-04-12T11:23:18.879736Z']
    x=data[1]
    data=[data[0], [str(i)[0:10] for i in x]]
    x = data[1]
    y = data[0]
    s = io.BytesIO()
    ax=sns.lineplot(x, y)
    ax.set_title('Your Wallet over time')
    ax.set_ylabel('Money')
    ax.set_xlabel('Time')
    # response = HttpResponse(content_type="image/jpeg")
    plt.plot()
    plt.savefig(s, format="png")
    plt.close()
    s = base64.b64encode(s.getvalue()).decode("utf-8").replace("\n", "")
    return HttpResponse("data:image/png;base64,%s"%s)
    
    # imgdata = StringIO()
    # fig.savefig(imgdata, format='svg')
    # imgdata.seek(0)

    # data = imgdata.getvalue()
    # return data

# def get_image():
#     s = io.BytesIO()
#     plt.plot(list(range(100)))
#     plt.savefig(s, format='png', bbox_inches="tight")
#     plt.close()
#     s = base64.b64encode(s.getvalue()).decode("utf-8").replace("\n", "")
#     return '<img align="left" src="data:image/png;base64,%s">' % s



