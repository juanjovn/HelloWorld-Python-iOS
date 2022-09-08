//
//  ContentView.swift
//  PythoniOS-Dummy
//
//  Created by Juanjo Valiño on 8/9/22.
//

import SwiftUI

struct ContentView: View {
    var body: some View {
        Text(String(runDummyPythonScript()) ?? "")
            .padding()
            .font(.title2)
            .frame(maxWidth: .infinity, alignment: .center)
    }
}

struct ContentView_Previews: PreviewProvider {
    static var previews: some View {
        ContentView()
    }
}
