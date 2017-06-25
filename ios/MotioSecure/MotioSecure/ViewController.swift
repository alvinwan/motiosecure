//
//  ViewController.swift
//  MotioSecure
//
//  Created by Alvin Wan on 6/24/17.
//  Copyright © 2017 Alvin Wan. All rights reserved.
//

import UIKit

class ViewController: UIViewController {
    
    var deviceTokenString: String = "";
    var viewInitialized: Bool = false;
    
    @IBOutlet weak var deviceTokenField: UITextView!
    
    override func viewDidLoad() {
        super.viewDidLoad()
        // Do any additional setup after loading the view, typically from a nib.
        setDeviceToken(deviceToken: deviceTokenString);
        viewInitialized = true;
    }

    override func didReceiveMemoryWarning() {
        super.didReceiveMemoryWarning()
        // Dispose of any resources that can be recreated.
    }
    
    func setDeviceToken(deviceToken: String) {
        if (viewInitialized) {
            deviceTokenField.text = deviceToken;
        } else {
            deviceTokenString = deviceToken;
        }
    }

    @IBAction func onTouchTestLiveFeed(_ sender: UIButton) {
        let url = URL(string: "facetime:youricloudemail@gmail.com")!
        UIApplication.shared.open(url)
    }

}

