//
//  PyTorchManager.swift
//  PythoniOS-Dummy
//
//  Created by Juanjo Valiño on 4/10/22.
//

import Foundation

class PyTorchManager {
    let modelName = "module_kp"
    let modelSignName = "module_kp_sign"
    lazy var module: VisionTorchModule = {
        guard let filePath = Bundle(for: type(of: self)).path(forResource: modelName, ofType: "pt") else { fatalError("error")}
        print(filePath)
        if let module = VisionTorchModule(fileAtPath: filePath) {
            return module
        } else {
            fatalError("Can't find the model file!")
        }
    }()
    
    lazy var moduleSign: VisionTorchModule = {
        if let filePath = Bundle.main.path(forResource: modelSignName, ofType: "pt"),
           let module = VisionTorchModule(fileAtPath: filePath) {
            return module
        } else {
            fatalError("Can't find the model file!")
        }
    }()
}
