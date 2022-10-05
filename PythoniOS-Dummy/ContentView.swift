//
//  ContentView.swift
//  PythoniOS-Dummy
//
//  Created by Juanjo Valiño on 8/9/22.
//

import SwiftUI

struct ContentView: View {
    
    func getString() -> String {
        let array = nummpyScript()
        var string = ""
        
        array.compactMap({
            String($0)
        })
        .forEach({string.append(contentsOf: "\($0) ")})
        
        return string
    }
    
    var body: some View {
        VStack {
            Text(getString())
                .padding()
                .font(.title2)
                .frame(maxWidth: .infinity, alignment: .center)
            
            Image(uiImage: generarImagen(for: machineLearningScript())!)
                .resizable()
                .aspectRatio(contentMode: .fit)
        }
    }
}

struct ContentView_Previews: PreviewProvider {
    static var previews: some View {
        ContentView()
    }
}
