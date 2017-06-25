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
    let emailAddressKey: String = "emailAddressKey";
    
    @IBOutlet weak var emailAddressField: UITextField!
    @IBOutlet weak var emailAddressStatusField: UILabel!
    @IBOutlet weak var liveFeedButton: UIButton!
    @IBOutlet weak var deviceTokenField: UITextView!
    
    override func viewDidLoad() {
        super.viewDidLoad()
        // Do any additional setup after loading the view, typically from a nib.
        setDeviceToken(deviceToken: deviceTokenString);
        let defaults = UserDefaults.standard;
        maybeEnableLiveFeedButton();
        viewInitialized = true;
        emailAddressField.text = defaults.string(forKey: emailAddressKey);
        emailAddressStatusField.text = "";
        self.hideKeyboardWhenTappedAround()
    }
    
    func maybeEnableLiveFeedButton() {
        let defaults = UserDefaults.standard;
        if ((defaults.string(forKey: emailAddressKey)) != nil) {
            liveFeedButton.isEnabled = true;
        } else {
            liveFeedButton.isEnabled = false;
        }
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

    @IBAction func onEnterEmailAddress(_ sender: UITextField) {
        onFinishEmailAddress(sender)
    }
    
    @IBAction func onTouchTestLiveFeed(_ sender: UIButton) {
        let defaults = UserDefaults.standard;
        let url = URL(string: "facetime:" + defaults.string(forKey: emailAddressKey)!)!
        UIApplication.shared.open(url)
    }

    @IBAction func onFinishEmailAddress(_ sender: UITextField) {
        let defaults = UserDefaults.standard;
        defaults.set(sender.text, forKey: emailAddressKey);
        liveFeedButton.isEnabled = true;
        emailAddressStatusField.text = "email saved";
    }
}

extension UIViewController {
    func hideKeyboardWhenTappedAround() {
        let tap: UITapGestureRecognizer = UITapGestureRecognizer(target: self, action: #selector(UIViewController.dismissKeyboard))
        tap.cancelsTouchesInView = false
        view.addGestureRecognizer(tap)
    }
    
    func dismissKeyboard() {
        view.endEditing(true)
    }
}

