# 🔗 EXEMPLOS DE INTEGRAÇÃO

Exemplos práticos de como integrar a API de Cardápio em diferentes linguagens e frameworks.

---

## 📱 JavaScript / Node.js

### Usando Fetch API
```javascript
async function gerarCardapio(arquivo) {
    const formData = new FormData();
    formData.append('file', arquivo);
    formData.append('font', 'Arial');
    formData.append('font_size', 10.0);

    try {
        // Upload
        const response = await fetch('http://localhost:8000/cardapio/gerar', {
            method: 'POST',
            body: formData
        });

        const data = await response.json();
        const jobId = data.job_id;

        // Aguardar conclusão
        const resultado = await aguardarConclusao(jobId);
        console.log('Cardápio gerado:', resultado);

        return resultado;
    } catch (error) {
        console.error('Erro:', error);
    }
}

async function aguardarConclusao(jobId) {
    while (true) {
        const response = await fetch(`http://localhost:8000/cardapio/status/${jobId}`);
        const status = await response.json();

        if (status.status === 'completed') {
            return status;
        } else if (status.status === 'failed') {
            throw new Error(status.message);
        }

        await new Promise(resolve => setTimeout(resolve, 2000));
    }
}

// Uso
const inputFile = document.getElementById('fileInput').files[0];
gerarCardapio(inputFile);
```

### Node.js com Axios
```javascript
const axios = require('axios');
const FormData = require('form-data');
const fs = require('fs');

async function gerarCardapio(caminhoArquivo) {
    const form = new FormData();
    form.append('file', fs.createReadStream(caminhoArquivo));
    form.append('font', 'Arial');
    form.append('font_size', 10.0);

    try {
        const response = await axios.post('http://localhost:8000/cardapio/gerar', form, {
            headers: form.getHeaders()
        });

        const jobId = response.data.job_id;
        console.log(`Job criado: ${jobId}`);

        // Polling
        while (true) {
            const statusRes = await axios.get(`http://localhost:8000/cardapio/status/${jobId}`);
            const status = statusRes.data;

            console.log(`Status: ${status.status}`);

            if (status.status === 'completed') {
                console.log('Concluído!');
                
                // Download PDF
                const pdfResponse = await axios.get(
                    `http://localhost:8000/cardapio/download/${jobId}/pdf`,
                    { responseType: 'stream' }
                );

                pdfResponse.data.pipe(fs.createWriteStream('cardapio.pdf'));
                break;
            } else if (status.status === 'failed') {
                throw new Error(status.message);
            }

            await new Promise(resolve => setTimeout(resolve, 2000));
        }
    } catch (error) {
        console.error('Erro:', error.message);
    }
}

// Uso
gerarCardapio('./teste_input.txt');
```

---

## 🐍 Python

### Usando Requests (Síncrono)
```python
import requests
import time
from pathlib import Path

def gerar_cardapio(caminho_arquivo):
    """Gera cardápio e aguarda conclusão"""
    
    # Upload
    with open(caminho_arquivo, 'rb') as f:
        files = {'file': f}
        data = {'font': 'Arial', 'font_size': 10.0}
        
        response = requests.post(
            'http://localhost:8000/cardapio/gerar',
            files=files,
            data=data
        )
    
    job_id = response.json()['job_id']
    print(f'Job ID: {job_id}')
    
    # Polling
    while True:
        status_response = requests.get(f'http://localhost:8000/cardapio/status/{job_id}')
        status = status_response.json()
        
        print(f"Status: {status['status']}")
        
        if status['status'] == 'completed':
            print('Concluído!')
            
            # Download PDF
            pdf_response = requests.get(
                f"http://localhost:8000/cardapio/download/{job_id}/pdf",
                stream=True
            )
            
            with open('cardapio.pdf', 'wb') as f:
                for chunk in pdf_response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            return status
        
        elif status['status'] == 'failed':
            raise Exception(status['message'])
        
        time.sleep(2)

# Uso
resultado = gerar_cardapio('teste_input.txt')
print(f"Arquivos: {resultado['files']}")
```

### Usando HTTPX (Assíncrono)
```python
import httpx
import asyncio

async def gerar_cardapio_async(caminho_arquivo):
    """Versão assíncrona"""
    
    async with httpx.AsyncClient() as client:
        # Upload
        with open(caminho_arquivo, 'rb') as f:
            files = {'file': f}
            data = {'font': 'Arial', 'font_size': 10.0}
            
            response = await client.post(
                'http://localhost:8000/cardapio/gerar',
                files=files,
                data=data
            )
        
        job_id = response.json()['job_id']
        print(f'Job ID: {job_id}')
        
        # Polling
        while True:
            status_response = await client.get(
                f'http://localhost:8000/cardapio/status/{job_id}'
            )
            status = status_response.json()
            
            if status['status'] == 'completed':
                return status
            elif status['status'] == 'failed':
                raise Exception(status['message'])
            
            await asyncio.sleep(2)

# Uso
resultado = asyncio.run(gerar_cardapio_async('teste_input.txt'))
```

---

## ☕ Java

### Usando OkHttp
```java
import okhttp3.*;
import org.json.JSONObject;
import java.io.File;
import java.io.FileOutputStream;
import java.io.IOException;
import java.util.concurrent.TimeUnit;

public class CardapioClient {
    private static final String API_URL = "http://localhost:8000";
    private static final OkHttpClient client = new OkHttpClient.Builder()
        .connectTimeout(30, TimeUnit.SECONDS)
        .readTimeout(30, TimeUnit.SECONDS)
        .build();

    public static String gerarCardapio(String caminhoArquivo) throws IOException {
        File file = new File(caminhoArquivo);

        RequestBody requestBody = new MultipartBody.Builder()
            .setType(MultipartBody.FORM)
            .addFormDataPart("file", file.getName(),
                RequestBody.create(file, MediaType.parse("text/plain")))
            .addFormDataPart("font", "Arial")
            .addFormDataPart("font_size", "10.0")
            .build();

        Request request = new Request.Builder()
            .url(API_URL + "/cardapio/gerar")
            .post(requestBody)
            .build();

        try (Response response = client.newCall(request).execute()) {
            JSONObject json = new JSONObject(response.body().string());
            return json.getString("job_id");
        }
    }

    public static JSONObject aguardarConclusao(String jobId) throws IOException, InterruptedException {
        while (true) {
            Request request = new Request.Builder()
                .url(API_URL + "/cardapio/status/" + jobId)
                .get()
                .build();

            try (Response response = client.newCall(request).execute()) {
                JSONObject status = new JSONObject(response.body().string());
                String statusStr = status.getString("status");

                System.out.println("Status: " + statusStr);

                if ("completed".equals(statusStr)) {
                    return status;
                } else if ("failed".equals(statusStr)) {
                    throw new RuntimeException(status.getString("message"));
                }
            }

            Thread.sleep(2000);
        }
    }

    public static void downloadPDF(String jobId, String outputPath) throws IOException {
        Request request = new Request.Builder()
            .url(API_URL + "/cardapio/download/" + jobId + "/pdf")
            .get()
            .build();

        try (Response response = client.newCall(request).execute()) {
            try (FileOutputStream fos = new FileOutputStream(outputPath)) {
                fos.write(response.body().bytes());
            }
        }
    }

    public static void main(String[] args) {
        try {
            String jobId = gerarCardapio("teste_input.txt");
            System.out.println("Job ID: " + jobId);

            JSONObject resultado = aguardarConclusao(jobId);
            System.out.println("Concluído!");

            downloadPDF(jobId, "cardapio.pdf");
            System.out.println("PDF baixado!");

        } catch (Exception e) {
            e.printStackTrace();
        }
    }
}
```

---

## 🔷 C# / .NET

### Usando HttpClient
```csharp
using System;
using System.IO;
using System.Net.Http;
using System.Threading;
using System.Threading.Tasks;
using Newtonsoft.Json.Linq;

public class CardapioClient
{
    private static readonly HttpClient client = new HttpClient();
    private const string API_URL = "http://localhost:8000";

    public static async Task<string> GerarCardapio(string caminhoArquivo)
    {
        using var form = new MultipartFormDataContent();
        
        var fileContent = new ByteArrayContent(File.ReadAllBytes(caminhoArquivo));
        fileContent.Headers.ContentType = new System.Net.Http.Headers.MediaTypeHeaderValue("text/plain");
        
        form.Add(fileContent, "file", Path.GetFileName(caminhoArquivo));
        form.Add(new StringContent("Arial"), "font");
        form.Add(new StringContent("10.0"), "font_size");

        var response = await client.PostAsync($"{API_URL}/cardapio/gerar", form);
        var json = await response.Content.ReadAsStringAsync();
        var obj = JObject.Parse(json);

        return obj["job_id"].ToString();
    }

    public static async Task<JObject> AguardarConclusao(string jobId)
    {
        while (true)
        {
            var response = await client.GetAsync($"{API_URL}/cardapio/status/{jobId}");
            var json = await response.Content.ReadAsStringAsync();
            var status = JObject.Parse(json);

            Console.WriteLine($"Status: {status["status"]}");

            if (status["status"].ToString() == "completed")
            {
                return status;
            }
            else if (status["status"].ToString() == "failed")
            {
                throw new Exception(status["message"].ToString());
            }

            await Task.Delay(2000);
        }
    }

    public static async Task DownloadPDF(string jobId, string outputPath)
    {
        var response = await client.GetAsync($"{API_URL}/cardapio/download/{jobId}/pdf");
        var bytes = await response.Content.ReadAsByteArrayAsync();
        
        File.WriteAllBytes(outputPath, bytes);
    }

    public static async Task Main(string[] args)
    {
        try
        {
            var jobId = await GerarCardapio("teste_input.txt");
            Console.WriteLine($"Job ID: {jobId}");

            var resultado = await AguardarConclusao(jobId);
            Console.WriteLine("Concluído!");

            await DownloadPDF(jobId, "cardapio.pdf");
            Console.WriteLine("PDF baixado!");
        }
        catch (Exception ex)
        {
            Console.WriteLine($"Erro: {ex.Message}");
        }
    }
}
```

---

## 🐘 PHP

### Usando cURL
```php
<?php

function gerarCardapio($caminhoArquivo) {
    $apiUrl = 'http://localhost:8000/cardapio/gerar';
    
    $cfile = new CURLFile($caminhoArquivo, 'text/plain', basename($caminhoArquivo));
    
    $data = [
        'file' => $cfile,
        'font' => 'Arial',
        'font_size' => '10.0'
    ];
    
    $ch = curl_init();
    curl_setopt($ch, CURLOPT_URL, $apiUrl);
    curl_setopt($ch, CURLOPT_POST, true);
    curl_setopt($ch, CURLOPT_POSTFIELDS, $data);
    curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
    
    $response = curl_exec($ch);
    curl_close($ch);
    
    $result = json_decode($response, true);
    return $result['job_id'];
}

function aguardarConclusao($jobId) {
    $apiUrl = 'http://localhost:8000/cardapio/status/' . $jobId;
    
    while (true) {
        $ch = curl_init();
        curl_setopt($ch, CURLOPT_URL, $apiUrl);
        curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
        
        $response = curl_exec($ch);
        curl_close($ch);
        
        $status = json_decode($response, true);
        
        echo "Status: " . $status['status'] . "\n";
        
        if ($status['status'] === 'completed') {
            return $status;
        } elseif ($status['status'] === 'failed') {
            throw new Exception($status['message']);
        }
        
        sleep(2);
    }
}

function downloadPDF($jobId, $outputPath) {
    $url = 'http://localhost:8000/cardapio/download/' . $jobId . '/pdf';
    
    $ch = curl_init();
    curl_setopt($ch, CURLOPT_URL, $url);
    curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
    
    $pdfContent = curl_exec($ch);
    curl_close($ch);
    
    file_put_contents($outputPath, $pdfContent);
}

// Uso
try {
    $jobId = gerarCardapio('teste_input.txt');
    echo "Job ID: $jobId\n";
    
    $resultado = aguardarConclusao($jobId);
    echo "Concluído!\n";
    
    downloadPDF($jobId, 'cardapio.pdf');
    echo "PDF baixado!\n";
    
} catch (Exception $e) {
    echo "Erro: " . $e->getMessage() . "\n";
}

?>
```

---

## 🦀 Rust

### Usando Reqwest
```rust
use reqwest::multipart::{Form, Part};
use serde_json::Value;
use std::fs::File;
use std::io::Write;
use std::time::Duration;
use tokio::time::sleep;

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    let job_id = gerar_cardapio("teste_input.txt").await?;
    println!("Job ID: {}", job_id);

    let resultado = aguardar_conclusao(&job_id).await?;
    println!("Concluído!");

    download_pdf(&job_id, "cardapio.pdf").await?;
    println!("PDF baixado!");

    Ok(())
}

async fn gerar_cardapio(caminho_arquivo: &str) -> Result<String, Box<dyn std::error::Error>> {
    let client = reqwest::Client::new();
    
    let file_content = std::fs::read(caminho_arquivo)?;
    let part = Part::bytes(file_content)
        .file_name("teste_input.txt")
        .mime_str("text/plain")?;
    
    let form = Form::new()
        .part("file", part)
        .text("font", "Arial")
        .text("font_size", "10.0");
    
    let response = client
        .post("http://localhost:8000/cardapio/gerar")
        .multipart(form)
        .send()
        .await?;
    
    let json: Value = response.json().await?;
    Ok(json["job_id"].as_str().unwrap().to_string())
}

async fn aguardar_conclusao(job_id: &str) -> Result<Value, Box<dyn std::error::Error>> {
    let client = reqwest::Client::new();
    
    loop {
        let response = client
            .get(&format!("http://localhost:8000/cardapio/status/{}", job_id))
            .send()
            .await?;
        
        let status: Value = response.json().await?;
        
        println!("Status: {}", status["status"]);
        
        match status["status"].as_str().unwrap() {
            "completed" => return Ok(status),
            "failed" => return Err(status["message"].as_str().unwrap().into()),
            _ => sleep(Duration::from_secs(2)).await,
        }
    }
}

async fn download_pdf(job_id: &str, output_path: &str) -> Result<(), Box<dyn std::error::Error>> {
    let client = reqwest::Client::new();
    
    let response = client
        .get(&format!("http://localhost:8000/cardapio/download/{}/pdf", job_id))
        .send()
        .await?;
    
    let bytes = response.bytes().await?;
    
    let mut file = File::create(output_path)?;
    file.write_all(&bytes)?;
    
    Ok(())
}
```

---

## 🔗 Webhook (Callback)

Se você quiser ser notificado quando o processamento terminar (em vez de fazer polling):

### Modificar a API
```python
# Adicionar no api_cardapio.py

from pydantic import HttpUrl

class CardapioConfig(BaseModel):
    font: str = "Arial"
    font_size: float = 10.0
    webhook_url: Optional[HttpUrl] = None  # <-- Nova opção

@app.post("/cardapio/gerar")
async def gerar_cardapio(
    ...,
    webhook_url: Optional[str] = None
):
    config = CardapioConfig(
        font=font,
        font_size=font_size,
        webhook_url=webhook_url
    )
    ...

# Modificar process_cardapio
def process_cardapio(job_id, input_path, config):
    try:
        # ... processamento ...
        
        # Ao concluir:
        if config.webhook_url:
            requests.post(config.webhook_url, json={
                "job_id": job_id,
                "status": "completed",
                "files": {...}
            })
    except Exception as e:
        if config.webhook_url:
            requests.post(config.webhook_url, json={
                "job_id": job_id,
                "status": "failed",
                "error": str(e)
            })
```

### Cliente com Webhook
```python
from flask import Flask, request

app = Flask(__name__)

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json
    print(f"Cardápio {data['job_id']}: {data['status']}")
    
    if data['status'] == 'completed':
        # Baixar arquivos
        ...
    
    return '', 200

# Enviar com webhook
requests.post('http://localhost:8000/cardapio/gerar',
    files={'file': open('teste_input.txt', 'rb')},
    data={'webhook_url': 'http://meu-servidor.com/webhook'}
)
```

---

**Integre facilmente em qualquer linguagem! 🚀**
