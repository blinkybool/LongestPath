using Google.OrTools.LinearSolver;
using System.Reflection.Metadata;

Solver solver = Solver.CreateSolver("CP-SAT");

int[,] graph = {
    { 0, 1 },
    { 1, 2 },
    { 2, 3 },
    { 2, 5 },
    { 1, 4 },
    { 3, 5 }
};

int n = 30;
int[,] AdjacencyMatrix = GraphReader.ReadGraph(GraphReader.RandomGraph(n, 2 * n));

/*
int[,] AdjacencyMatrix = {
    { 0,1,0,0,0,0 },
    { 1,0,1,0,1,0 },
    { 0,1,0,1,0,1 },
    { 0,0,1,0,0,0 },
    { 0,1,0,0,0,0 },
    { 0,0,1,0,0,0 }
};
*/

int VertexAmount = AdjacencyMatrix.GetLength(0);
int PathPlaces = VertexAmount;

Variable[,] variables = new Variable[PathPlaces, VertexAmount + 1];

for (int vert = 0; vert < VertexAmount + 1; vert++)
{
    for (int place = 0; place < PathPlaces; place ++)
    {
        variables[place, vert] = solver.MakeBoolVar("X{" + place.ToString() + ", " + vert.ToString() + "}");
    }
}

//Define cost function
LinearExpr linExpr = new LinearExpr();
for ( int place = 0; place < PathPlaces; place++)
{
    LinearExpr l = new LinearExpr();
    for (int vert = 0; vert < VertexAmount; vert++)
    {
        l += variables[place, vert];
    }
    linExpr += l;
}
solver.Maximize(linExpr);

//No repeated use of vertices restriction
for (int vert = 0; vert < VertexAmount; vert++)
{
    linExpr = new LinearExpr();

    for (int place = 0; place < PathPlaces; place++)
    {
        linExpr += variables[place, vert];
    }
    solver.Add(linExpr <= 1);
}


//Only use one vertex per time block.
for (int place = 0; place < PathPlaces; place++)
{
    linExpr = new LinearExpr();

    for (int vert = 0; vert < VertexAmount + 1; vert++)
    {
        linExpr += variables[place, vert];
    }
    solver.Add(linExpr == 1);
}


for (int place = 0; place < PathPlaces - 1; place++)
{
    for (int vert1 = 0; vert1 < VertexAmount + 1; vert1++)
    {
        for (int vert2 = 0; vert2 < VertexAmount + 1; vert2++)
        {
            if(vert1 == VertexAmount)
            {
                if (vert2 != VertexAmount)
                {
                    solver.Add(variables[place, vert1] + variables[place + 1, vert2] <= 1);
                }
            }
            else
            {
                if(vert2 != VertexAmount && vert1 != vert2)
                {
                    if (AdjacencyMatrix[vert1, vert2] ==0)
                    {
                        solver.Add(variables[place, vert1] + variables[place + 1, vert2] <= 1);
                    }
                }
            }

        }
    }
}

var watch = new System.Diagnostics.Stopwatch();
watch.Start();

Solver.ResultStatus resultStatus = solver.Solve();

watch.Stop();

// Check that the problem has an optimal solution.
if (resultStatus != Solver.ResultStatus.OPTIMAL)
{
    Console.WriteLine("The problem does not have an optimal solution!");
    return;
}
Console.WriteLine("Solution:");
Console.WriteLine("Objective value = " + solver.Objective().Value());
for (int place = 0; place < PathPlaces; place++)
{
    for (int vert = 0; vert < VertexAmount + 1; vert++)
    {
        Console.WriteLine("X{" + place.ToString() + ", " + vert.ToString() + "}" + " = " + variables[place, vert].SolutionValue());
    }
}
Console.WriteLine("Objective value = " + solver.Objective().Value());
Console.WriteLine($"Execution Time: {watch.ElapsedMilliseconds} ms");