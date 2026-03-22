import rclpy
from geometry_msgs.msg import Twist
from rclpy.node import Node
from std_msgs.msg import String


class EnergyNode(Node):
    def __init__(self):
        super().__init__('minimal_subscriber')
        self.energy = 100
        self.linear_a = Twist()
        self.angular_a =Twist()
        self.linear_f = Twist()
        self.angular_f = Twist()
        self.fm = 5
        self.bm = 8
        self.rm = 3

        self.grid_x = 1 #assuming the grid is a square with side length 1
        self.pi_on_4 = 3.14159265358/4
        self.subscription = self.create_subscription(
            Twist,
            'cmd_vel',
            self.listener_callback,
            10)
        self.subscription  # prevent unused variable warning
        self.publisher = self.create_publisher(String, 'Energy', 10)
        self.timer = self.create_timer(1, self.timer_callback)

    def listener_callback(self, msg):
        self.get_logger().info('linear "%s"' % msg.linear.x)
        self.get_logger().info('Angular "%s"' % msg.angular.x)
        self.linear_f = msg.linear
        self.angular_f = msg.angular

    def timer_callback(self):
        msg = String()
        msg.data = f"{self.energy} EU"
        self.publisher.publish(msg)
        # self.get_logger().info(f'Publishing energy level :{self.energy} Eu')

    def calc_enery_loss(self):
        #define when it is starting and stopping and apply energy charges
        #multiply the speed by the loss per unit time to get standard loss 
        self.lina_tot = self.linear_a.x + self.linear_a.y + self.linear_a.z
        self.anga_tot = self.angular_a.x + self.angular_a.y + self.angular_a.z
        self.linf_tot = self.linear_f.x + self.linear_f.y + self.linear_f.z
        self.angf_tot = self.angular_f.x + self.angular_f.y + self.angular_f.z

        if (not self.lina_tot and self.linf_tot) or (not self.anga_tot and self.angf_tot) :
            self.get_logger().info("The robot is starting")
            self.energy -= 1
        
        if (self.lina_tot and not self.linf_tot) or (self.anga_tot and not self.angf_tot) :
            self.get_logger().info("The robot is stopping")
            self.energy -= 0.5

        self.tot_rot_loss = self.rm*(self.angf_tot)/self.pi_on_4
        self.tot_lin_loss = self.linf_tot*(5 if self.linf_tot>0 else 8)/self.grid_x
        
        self.energy -= self.tot_rot_loss + self.tot_lin_loss

        self.linear_a = self.linear_f
        self.angular_a = self.angular_f



def main(args=None):
    rclpy.init(args=args)

    minimal_subscriber = EnergyNode()

    rclpy.spin(minimal_subscriber)

    # Destroy the node explicitly
    # (optional - otherwise it will be done automatically
    # when the garbage collector destroys the node object)
    minimal_subscriber.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
