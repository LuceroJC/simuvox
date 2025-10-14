
class RegularizedExtremum(object) :
  
      def __init__(self, max_eps, min_eps) :

            '''
            max_eps = fraction of the amplitude during which regularization is applied in max()
            min_eps = fraction of the amplitude during which regularization is applied in min()
            '''


            self.__max_eps = max_eps
            self.__min_eps = min_eps

            
      def get_regularized_min(self, a, b) :
           
            '''
            regularized min
            implies some undershoot via a parabola that replaces the abs() operator when x < eps
            for regularization purposes
            since it is used as a projector, the regularization is only applied
            when a and b are large
            '''

            x     = a - b
            abs_x = abs(x)
            
            yop = 0.5 * (a + b - abs_x)

            if abs_x < self.__min_eps and a > self.__min_eps and b > self.__min_eps :
                  abs_x = (0.5 / self.__min_eps) * x**2 + 0.5 * self.__min_eps
                  yop = 0.5 * (a + b - abs_x)
            
            return yop

      def get_regularized_max(self, a, b) :

            '''
            regularized max
            implies some undershoot via a parabola that replaces for regularization purposes
            abs() when x < eps, since it is used as a collision operator, the regularization
            is only applied when a and b are almost equal 
            '''
            x     = a - b
            abs_x = abs(x)
            
            yop = 0.5 * (a + b + abs_x)
            
            if abs_x < self.__max_eps :
                  abs_x = (0.5 / self.__max_eps) * x**2 + 0.5 * self.__max_eps
                  yop   = 0.5 * (a + b + abs_x)
            return yop



      def test_regularized_extremum(self, a, b) :

            min_a_b = self.get_regularized_min(a, b)
            max_a_b = self.get_regularized_max(a, b)

            print("min =", min_a_b)
            print("max =", max_a_b)

      
