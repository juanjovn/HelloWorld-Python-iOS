//
//  PythonManager.swift
//  PythoniOS-Dummy
//
//  Created by Juanjo Valiño on 8/9/22.
//

import Foundation
import PythonKit
import NumPySupport
import PythonSupport

func runDummyPythonScript() -> PythonObject {
    
    let bundlePath = Bundle.main.bundlePath
    
    PythonSupport.initialize()
    let sys = Python.import("sys")
    sys.path.append(bundlePath)
    let module = Python.import("DummyPythonScript")
    let message = module.hello_world()

    return message
}

func nummpyScript() -> PythonObject {
    let bundlePath = Bundle.main.bundlePath
    
    PythonSupport.initialize()
    NumPySupport.sitePackagesURL.insertPythonPath()
    let sys = Python.import("sys")
    sys.path.append(bundlePath)
    let module = Python.import("DummyPythonScript")
    let message = module.numpy_dummy()
    print(message)

    return message
}
