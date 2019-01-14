"""
-------------------------------------------------------
This file contains and defines the Retailer class.
-------------------------------------------------------
Author:  Tom LaMantia
Email:   tom@lamantia.mail.utoronto.ca
Version: February 7th 2016
-------------------------------------------------------
"""

from SupplyChainActor import SupplyChainActor , SupplyChainQueue
import numpy as np





class Retailer(SupplyChainActor):
    
    def __init__(self, policy, nstates , initial_stock , incomingOrdersQueue, outgoingOrdersQueue, incomingDeliveriesQueue, outgoingDeliveriesQueue, theCustomer):
        """
        -------------------------------------------------------
        Constructor for the Retailer class.
        -------------------------------------------------------
        Preconditions: incomingOrdersQueue, outgoingOrdersQueue, incomingDeliveriesQueue, outgoingDeliveriesQueue - 
                the supply chain queues. Note: outgoingDeliveriesQueue and incomingOrdersQueue should be NONE.
                
                theCustomer - a customer object.
        Postconditions:
            Initializes the retailer object in its initial state
            by calling parent constructor and setting the
            retailer's customer.
        -------------------------------------------------------
        """
        super().__init__(policy , nstates, initial_stock , incomingOrdersQueue, outgoingOrdersQueue, incomingDeliveriesQueue, outgoingDeliveriesQueue)
        self.customer = theCustomer


        return


    
    def ReceiveIncomingOrderFromCustomer(self, weekNum):
        """
        -------------------------------------------------------
        Receives an order from the customer.
        -------------------------------------------------------
        Preconditions: weekNum - the current week.
        Postconditions:
            Adds the customer's order to the current orders.
        -------------------------------------------------------
        """
        new_order = self.customer.CalculateOrder(weekNum)
        self.currentOrders += new_order
        return new_order
    
    def ShipOutgoingDeliveryToCustomer(self):
        """
        -------------------------------------------------------
        Ships an order from the customer.
        -------------------------------------------------------
        Preconditions: None
        Postconditions: Calculates the amount of beer to be delivered
            based on the current stock. This is then added to the customer's
            total beer received. 
        -------------------------------------------------------
        """
        self.customer.RecieveFromRetailer(self.CalcBeerToDeliver())
        return
    
    def TakeTurn(self, weekNum):
        
        #The steps for taking a turn are as follows:
        

        #RECEIVE NEW DELIVERY FROM WHOLESALER
        old_stock = self.currentStock
        new_shipment = self.ReceiveIncomingDelivery()    #This also advances the queue!
        
        
        #RECEIVE NEW ORDER FROM CUSTOMER
        old_orders = self.currentOrders
        new_orders = self.ReceiveIncomingOrderFromCustomer(weekNum)



        ##############################################
        # ----------------- STATE --------------------
        # We constitute the state of the player
        curr_state = [old_stock , new_shipment , old_orders , new_orders]
        # Incoming Deliveries
        curr_state.extend(self.outgoingOrdersQueue.data[:1])
        self.states.append(curr_state) 
        state = self.states[-self.nstates:]
        if len(state) < self.nstates : state = [[-1 , -1 , -1 , -1 , -1]]*(self.nstates - len(state)) + state
        # --------------------------------------------
        ##############################################


        #CALCULATE AMOUNT TO BE SHIPPED, THEN SHIP IT
        #self.ShipOutgoingDeliveryToCustomer()
        self.customer.RecieveFromRetailer(self.CalcBeerToDeliver())
        
        #PLACE ORDER TO WHOLESALER
        policy_action = self.PlaceOutgoingOrder(state)
        

        #UPDATE COSTS
        self.costsIncurred += self.CalcCostForTurn()


        
        return state , policy_action , -1*self.CalcCostForTurn()




##############################################################################################


class Customer:

    def __init__(self , orders , max_noise = 0):
        """
        -------------------------------------------------------
        Constructor for the Customer class.
        -------------------------------------------------------
        Preconditions: None
        Postconditions:
            Initializes the Customer object in its initial state.
        -------------------------------------------------------
        """
        self.totalBeerReceived = 0
        self.orders = orders
        self.max_noise = max_noise
        return
    
    def RecieveFromRetailer(self, amountReceived):
        """
        -------------------------------------------------------
        Receives stock from the retailer.
        -------------------------------------------------------
        Preconditions: amountReceived - the number of cases shipped to the
                    customer by the retailer.
        Postconditions:
            Increments totalBeerReceived accordingly.
        -------------------------------------------------------
        """
        self.totalBeerReceived += amountReceived
        
        return
    
    def CalculateOrder(self, weekNum):
        """
        -------------------------------------------------------
        Calculates the amount of stock to order from the retailer.
        -------------------------------------------------------
        Preconditions: weekNum - the current week of game-play.
        Postconditions:
            The customer orders 4 cases on weeks 1-5, and 8 cases 
            for all other weeks. 
        -------------------------------------------------------
        """
        cnorder = self.orders[weekNum] + np.random.choice(self.max_noise) if self.max_noise > 0 else self.orders[weekNum]
        return cnorder
    
    def GetBeerReceived(self):
        """
        -------------------------------------------------------
        Returns the total beer received by the customer.
        -------------------------------------------------------
        Preconditions: None.
        Postconditions: Returns totalBeerReceived
        -------------------------------------------------------
        """
        return self.totalBeerReceived





##############################################################################################







class Wholesaler(SupplyChainActor):
    
    def __init__(self, policy, nstates , initial_stock , incomingOrdersQueue, outgoingOrdersQueue, incomingDeliveriesQueue, outgoingDeliveriesQueue):
        """
        -------------------------------------------------------
        Constructor for the Wholesaler class.
        -------------------------------------------------------
        Preconditions: incomingOrdersQueue, outgoingOrdersQueue, incomingDeliveriesQueue, outgoingDeliveriesQueue - 
                the supply chain queues.
        Postconditions:
            Initializes the Wholesaler object in its initial state
            by calling parent constructor.
        -------------------------------------------------------
        """
        super().__init__(policy , nstates, initial_stock , incomingOrdersQueue, outgoingOrdersQueue, incomingDeliveriesQueue, outgoingDeliveriesQueue)
        return
    
    def TakeTurn(self, weekNum):
        
        #The steps for taking a turn are as follows:
        
        #RECEIVE NEW DELIVERY FROM DISTRIBUTOR
        old_stock = self.currentStock
        new_shipment = self.ReceiveIncomingDelivery()    #This also advances the queue!
        
        #RECEIVE NEW ORDER FROM RETAILER
        old_orders = self.currentOrders
        new_orders = self.ReceiveIncomingOrders()     #This also advances the queue!




        ##############################################
        # ----------------- STATE --------------------
        # We constitute the state of the player
        curr_state = [old_stock , new_shipment , old_orders , new_orders]
        # Incoming Deliveries
        curr_state.extend(self.outgoingOrdersQueue.data[:1])
        self.states.append(curr_state) 
        state = self.states[-self.nstates:]
        if len(state) < self.nstates : state = [[-1 , -1 , -1 , -1 , -1]]*(self.nstates - len(state)) + state
        # --------------------------------------------
        ##############################################


        
        #PREPARE DELIVERY
        self.PlaceOutgoingDelivery(self.CalcBeerToDeliver())
    
        #PLACE ORDER
        policy_action = self.PlaceOutgoingOrder(state)
        
        #UPDATE COSTS
        self.costsIncurred += self.CalcCostForTurn()
        
        return state , policy_action , -1*self.CalcCostForTurn()







##############################################################################################





class Distributor(SupplyChainActor):
    
    def __init__(self, policy, nstates , initial_stock , incomingOrdersQueue, outgoingOrdersQueue, incomingDeliveriesQueue, outgoingDeliveriesQueue):
        """
        -------------------------------------------------------
        Constructor for the Distributor class.
        -------------------------------------------------------
        Preconditions: incomingOrdersQueue, outgoingOrdersQueue, incomingDeliveriesQueue, outgoingDeliveriesQueue - 
                the supply chain queues.
        Postconditions:
            Initializes the Distributor object in its initial state
            by calling parent constructor.
        -------------------------------------------------------
        """
        super().__init__(policy , nstates, initial_stock , incomingOrdersQueue, outgoingOrdersQueue, incomingDeliveriesQueue, outgoingDeliveriesQueue)
        return
    
    
    def TakeTurn(self, weekNum):
        
        #The steps for taking a turn are as follows:
        
        #RECEIVE NEW DELIVERY FROM FACTORY
        old_stock = self.currentStock
        new_shipment = self.ReceiveIncomingDelivery()    #This also advances the queue!
        
        #RECEIVE NEW ORDER FROM WHOLESALER
        old_orders = self.currentOrders
        new_orders = self.ReceiveIncomingOrders()     #This also advances the queue!



        ##############################################
        # ----------------- STATE --------------------
        # We constitute the state of the player
        curr_state = [old_stock , new_shipment , old_orders , new_orders]
        # Incoming Deliveries
        curr_state.extend(self.outgoingOrdersQueue.data[:1])
        self.states.append(curr_state) 
        state = self.states[-self.nstates:]
        if len(state) < self.nstates : state = [[-1 , -1 , -1 , -1 , -1]]*(self.nstates - len(state)) + state
        # --------------------------------------------
        ##############################################


        
        #PREPARE DELIVERY
        self.PlaceOutgoingDelivery(self.CalcBeerToDeliver())
        
        #PLACE ORDER
        policy_action = self.PlaceOutgoingOrder(state)
        
        #UPDATE COSTS
        self.costsIncurred += self.CalcCostForTurn()
        
        return state , policy_action , -1*self.CalcCostForTurn()






##############################################################################################






class Factory(SupplyChainActor):
    
    def __init__(self, policy, nstates , initial_stock , incomingOrdersQueue, outgoingOrdersQueue, incomingDeliveriesQueue, outgoingDeliveriesQueue, factoryProductionDelayQueue):
        """
        -------------------------------------------------------
        Constructor for the Factory class.
        -------------------------------------------------------
        Preconditions: incomingOrdersQueue, outgoingOrdersQueue, incomingDeliveriesQueue, outgoingDeliveriesQueue - 
                the supply chain queues. Note: outgoingOrdersQueue and incomingDeliveriesQueue should be NONE.
                productionDelayWeeks - an integer value indicating the nunber of weeks required to make a case of beer.
        Postconditions:
            Initializes the Factory object in its initial state
            by calling parent constructor and setting the
            retailer's customer.
        -------------------------------------------------------
        """
        super().__init__(policy , nstates, initial_stock , incomingOrdersQueue, outgoingOrdersQueue, incomingDeliveriesQueue, outgoingDeliveriesQueue)
        self.BeerProductionDelayQueue = factoryProductionDelayQueue
        
        return
    
    def ProduceBeer(self, state):
        """
        -------------------------------------------------------
        Calculates the size of this week's production run.
        -------------------------------------------------------
        Preconditions:  weekNum - the current week number.
        Postconditions:
            Calculates the production run using an anchor and maintain
            strategy.
        -------------------------------------------------------
        """
            
        amountToOrder , policy_action  = self.policy.calculate_order( state )
        self.BeerProductionDelayQueue.PushEnvelope(amountToOrder)
        self.lastOrderQuantity = amountToOrder
        
        return policy_action
    
    def FinishProduction(self):
        """
        -------------------------------------------------------
        Finishes production by popping the production queue and
        adding this beer to the current stock of the factory.
        -------------------------------------------------------
        Preconditions:  None
        Postconditions: Updates currentStock to reflect the beer
            that the factory just brewed.
        -------------------------------------------------------
        """
        amountProduced = self.BeerProductionDelayQueue.PopEnvelope()
        
        if amountProduced > 0:
            self.currentStock += amountProduced
        
        return amountProduced
     
    def TakeTurn(self, weekNum):
        
        #The steps for taking a turn are as follows:
        
        #PREVIOUS PRODUCTION RUNS FINISH BREWING.
        old_stock = self.currentStock
        new_shipment = self.FinishProduction()
        
        #RECEIVE NEW ORDER FROM DISTRIBUTOR
        old_orders = self.currentOrders
        new_orders = self.ReceiveIncomingOrders()     #This also advances the queue!



        ##############################################
        # ----------------- STATE --------------------
        # We constitute the state of the player
        curr_state = [old_stock , new_shipment , old_orders , new_orders]
        # Incoming Deliveries
        curr_state.extend(self.BeerProductionDelayQueue.data[:1])
        self.states.append(curr_state)
        state = self.states[-self.nstates:]
        if len(state) < self.nstates : state = [[-1 , -1 , -1 , -1 , -1]]*(self.nstates - len(state)) + state
        # --------------------------------------------
        ##############################################


        
        #PREPARE DELIVERY
        self.PlaceOutgoingDelivery(self.CalcBeerToDeliver())
        
        #PRODUCE BEER
        policy_action = self.ProduceBeer(state)
        
        #UPDATE COSTS
        self.costsIncurred += self.CalcCostForTurn()
        
        return state , policy_action , -1*self.CalcCostForTurn()

