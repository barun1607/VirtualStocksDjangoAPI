import io
import base64
import seaborn as sns
import matplotlib.pyplot as plt
from io import StringIO
import numpy as np
from django.http import HttpResponse


# @api_view(['GET'])
# @authentication_classes([TokenAuthentication])
# @permission_classes([IsAuthenticated])
# def plot_graph():
#     plt.show()




def return_graph(data):
    print(data)
    sns.set()
    sns.set_theme(style="darkgrid")
    x = data[0]
    y = data[1]
    ax=sns.lineplot(x, y)
    ax.set_title('Your Wallet over time')
    ax.set_ylabel('Money')
    ax.set_xlabel('Time')
    response = HttpResponse(content_type="image/jpeg")
    plt.savefig(response, format="png")
    return response    
    
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



