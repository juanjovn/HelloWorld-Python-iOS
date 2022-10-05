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
import UIKit

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
    machineLearningScript()
    
    return message
}

func machineLearningScript() -> [[Double]] {
    let bundlePath = Bundle.main.bundlePath
    var jsonData = Data()
    var jsonString = ""
    guard let jsonPath = Bundle.main.path(forResource: "ejemplo-angel", ofType: "json") else { return [[]]}
    do {
        jsonData = try String(contentsOfFile: jsonPath).data(using: .utf8) ?? Data()
        jsonString = try String(contentsOfFile: jsonPath, encoding: .utf8)
        print(jsonString)
    } catch {
        print(error)
    }
    PythonSupport.initialize()
    NumPySupport.sitePackagesURL.insertPythonPath()
    let sys = Python.import("sys")
    sys.path.append(bundlePath)
    let module = Python.import("kwikpen-python-script")
    //    let pythonResult = module.clean_all_zeros([1,2,3,0],[1,2,3,0])
    let pythonResult = module.prepare(jsonString)
    let matriz: [[Double]] = Array(pythonResult[0])!
    let matrizPrueba: [[Double]] = [[0,1,2,3,4,5],[0,1,2,3,4,5],[0,1,2,3,4,5],[0,1,2,3,4,5,9999.9999]]
    print(matriz)
    print("Valor maximo de matriz: \(maxMatriz(for: matriz))")
    print("Valor minimo de matriz: \(minMatriz(for: matriz))")
    print("Count de la matriz: \(matriz.count)")
    print(pythonResult[0])
    
    return matriz
}

func maxMatriz(for matrix: [[Double]]) -> Double {
    var maxValues: [Double] = []
    matrix.forEach({ values in
        let maximo = values.sorted(by: >)
            .max()
        maxValues.append(maximo ?? 0)
    })
    
    return maxValues.max() ?? 0
}

func minMatriz(for matrix: [[Double]]) -> Double {
    var minValues: [Double] = []
    matrix.forEach({ values in
        let minimo = values.sorted(by: <)
            .min()
        minValues.append(minimo ?? 0)
    })
    
    return minValues.min() ?? 0
}

func generarImagen(for matrix: [[Double]]) -> UIImage? {
    let width = matrix[0].count
    let height = matrix.count
    let numberOfPixels = width * height
    //    print("⊹ Matrix: \(matrix)")
    print("📐 Width: \(width)")
    print("📐 Height \(height)")
    print("🔢 Number of pixels \(numberOfPixels)")
    var pixels = [UInt32]()
    
    let max = maxMatriz(for: matrix)
    let min = minMatriz(for: matrix)
    
    matrix.forEach(
        {
            $0.forEach({
                pixels.append(getColor(min: min, max: max, value: $0))
            })
        }
    )
    //    print("🚥 \(pixels)")
    
    return createImage(from: pixels, width: width, height: height)
}

func getColor(min: Double, max: Double, value: Double) -> UInt32 {
    print("📥 Value: \(value)")
    let gray = UInt8((value * 255)) & 0xFF
    let cgGray = CGFloat(gray)
    let intGray = Int(gray)
    print("◻️ Gray \(gray)")
    let colorRgb = colorRgb(red: intGray, green: intGray, blue: intGray)
    print("🔥 Prueba: \(colorRgb)")
    
    let ciColor = CIColor(red: cgGray, green: cgGray, blue: cgGray)
    let uiColor = UIColor(ciColor: ciColor)
    let hexValue = UInt32(uiColor.hex)
    print("➡️ HEX value: \(hexValue)")
    
    //    let pixelColor = Int(UIColor(ciColor: CIColor(red: gray, green: gray, blue: gray)).hex)
    //    let pixelColor = Int(UIColor(red: gray, green: gray, blue: gray, alpha: 1).hex)
    
    //    let pixelData = PixelData(a: 1, r: gray, g: gray, b: gray)
    //    print("🎨 Pixel Data: \(pixelData)")
    
    return colorRgb
}

func colorRgb(red: Int, green: Int, blue: Int) -> UInt32 {
    let num = 0xFF000000  | UInt32(red << 16) | UInt32(green << 8) | UInt32(blue)
    //    let x = Int32(bitPattern: num)
    
    //    return Int(x)
    return num
}

func createImage(from pixels: [UInt32], width: Int, height: Int ) -> UIImage? {
    guard let image = mask(from: pixels, width: width, height: height) else { return nil }
    
    // TESTING PREDICTION - MOVE LATER
    let prediction = predict(for: transformImage(with: image))
    print("🔮 PREDICTION: \(prediction)")
    // *********
    
    return image
}

func mask(from data: [UInt32], width: Int, height: Int) -> UIImage? {
    var srgbArray = [UInt32]()
    data.forEach({srgbArray.append($0)})
    print(srgbArray)
    
    let cgImg = srgbArray.withUnsafeMutableBytes { (ptr) -> CGImage in
        let ctx = CGContext(
            data: ptr.baseAddress,
            width: width,
            height: height,
            bitsPerComponent: 8,
            bytesPerRow: 4 * width,
            space: CGColorSpace(name: CGColorSpace.sRGB)!,
            bitmapInfo: CGBitmapInfo.byteOrder32Little.rawValue +
            CGImageAlphaInfo.premultipliedFirst.rawValue
        )!
        return ctx.makeImage()!
    }
    
    return UIImage(cgImage: cgImg)
}

func predict(for imageData: [Float32]) -> [Double] {
    let pytorchManager = PyTorchManager()
    let module = pytorchManager.module
    let moduleSign = pytorchManager.moduleSign
    var pixelBuffer = imageData
    
    guard let outputs = module.predict(image: UnsafeMutableRawPointer(&pixelBuffer)) else { return [] }
    
    var castedOutputs = [Double]()
    
    for output in outputs {
        castedOutputs.append(output as! Double)
    }
    
    return castedOutputs.sorted(by: >)
}

func transformImage(with image: UIImage) -> [Float32] {
    guard let image = image.normalized() else { return [] }
    
    return image
}

extension UIColor {
    var coreImageColor: CIColor {
        return CIColor(color: self)
    }
    var hex: UInt {
        let red = UInt(coreImageColor.red * 255 + 0.5)
        let green = UInt(coreImageColor.green * 255 + 0.5)
        let blue = UInt(coreImageColor.blue * 255 + 0.5)
        return (red << 16) | (green << 8) | blue
    }}
