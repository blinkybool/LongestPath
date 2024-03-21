using System;
using System.Collections.Generic;
using System.Linq;
using System.Numerics;
using System.Text;
using System.Threading.Tasks;

class GraphReader    
{
    public static int[,] ReadGraph(int[,] connections)
    {
        int MaxIndex = 0;
        for(int i = 0; i < connections.GetLength(0); i++)
        {
            if (connections[i,0] > MaxIndex)
            {
                MaxIndex = connections[i,0];
            }
            if (connections[i, 1] > MaxIndex)
            {
                MaxIndex = connections[i, 1];
            }
        }
        Console.WriteLine("Graph has " + (MaxIndex + 1) + " vertices.");

        int[,] output = new int[MaxIndex + 1, MaxIndex + 1];
        for(int i = 0; i < connections.GetLength(0); i++)
        {
            output[connections[i, 0], connections[i, 1]] = 1;
            output[connections[i, 1], connections[i, 0]] = 1;
        }

        return output;
    }    

    public static int[,] LineGraph(int n)
    {
        int[,] graph = new int[n-1,2];
        for (int i = 0; i < n-1; i++)
        {
            graph[i, 0] = i;
            graph[i, 1] = i + 1;
        }

        return graph;
    }

    public static int[,] RandomGraph(int n, int m)
    {
        Random random = new Random();

        int[,] graph = new int[m, 2];
        graph[m - 1, 0] = 0;
        graph[m - 1, 1] = n-1;

        for (int i = 0; i < m - 2; i++)
        {
            int k = random.Next(n);
            int l = random.Next(n);

            while (k == l)
            {
                l = random.Next(n);
            }

            graph[i, 0] = k;
            graph[i, 1] = l;
        }

        return graph;
    }

    public static int[,] ForkGraph(int n)
    {
        int[,] graph = new int[((n - 2) * (n - 1) / 2) + n-1 , 2];

        int k = 0;
        int b = 1;
        for(int i = 0; i < n-1; i++)
        {
            int offset = 0;
            if (i == 0)
                offset = 1;
            else
                offset = i;

            graph[k, 0] = b - offset;
            graph[k, 1] = b;
            k++;

            for(int j = 0; j < i; j++)
            {
                graph[k, 0] = b + j;
                graph[k, 1] = b + j + 1;
                k++;
            }
            b += i + 1;
        }

        return graph;
    }

}
