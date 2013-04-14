using System;

namespace Forseti
{
    public class CubeRouteField
    {

        public CubeRouteField (GoalFlags[] goals)
        {
            this.Goals = goals;
        }

        public GoalFlags[] Goals
        {
            private set;
            get;
        }
    }
}

