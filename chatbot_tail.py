            # Filter out low similarity results
            relevant_knowledge = []
            for idx in top_indices:
                if similarities[idx] > 0.1:  # Threshold for relevance
                    relevant_knowledge.append({
                        'knowledge': self.knowledge_base[idx],
                        'similarity': float(similarities[idx])
                    })
            
            return relevant_knowledge
            
        except Exception as e:
            print(f"Error finding relevant knowledge: {e}")
            return []
    
    def _generate_rag_response(self, query, relevant_knowledge):
        """Generate response using retrieved knowledge and Gemini"""
        if not relevant_knowledge:
            if GEMINI_AVAILABLE:
                # If no specific knowledge found, let Gemini answer with general knowledge but with a disclaimer
                try:
                    prompt = f"""
                    You are an Ayurvedic expert assistant for Prakriti Pulse.
                    User Query: {query}
                    
                    Please answer the query based on general Ayurvedic principles. 
                    Disclaimer: Mention that this is general information and they should consult a practitioner.
                    """
                    response = self.gemini_model.generate_content(prompt)
                    return response.text
                except Exception as e:
                    return "I don't have specific information about that. You might want to consult with an Ayurvedic practitioner for personalized advice."
            return "I don't have specific information about that. You might want to consult with an Ayurvedic practitioner for personalized advice."
        
        # Prepare context from relevant knowledge
        context_parts = []
        for item in relevant_knowledge:
            knowledge = item['knowledge']
            context_parts.append(f"--- Info (Type: {knowledge.get('type', 'General')}) ---\n{knowledge['text']}")
        
        context = "\n\n".join(context_parts)
        
        if GEMINI_AVAILABLE:
            try:
                # Construct prompt carefully to avoid syntax errors
                prompt = "You are an Ayurvedic expert assistant for Prakriti Pulse.\n"
                prompt += "Use the following context to answer the user's question.\n\n"
                prompt += f"Context:\n{context}\n\n"
                prompt += f"User Query: {query}\n\n"
                prompt += "Instructions:\n"
                prompt += "1. Answer the query using ONLY the provided context if possible.\n"
                prompt += "2. If the context doesn't fully answer it, you can use your general knowledge but prioritize the context.\n"
                prompt += "3. Format the response with HTML tags for better readability (e.g., <b>, <ul>, <li>, <p>).\n"
                prompt += "4. Be helpful, empathetic, and professional.\n"
                prompt += "5. If recommending herbs, mention contraindications if available in context.\n"
                
                response = self.gemini_model.generate_content(prompt)
                return response.text
            except Exception as e:
                print(f"Gemini generation error: {e}")
                # Fallback to manual response generation
        
        # Fallback manual response generation (existing logic)
        response_parts = []
        
        # Sort by similarity
        relevant_knowledge.sort(key=lambda x: x['similarity'], reverse=True)
        
        # Generate response based on knowledge type
        herbs_mentioned = []
        symptoms_mentioned = []
        prakriti_types = []
        
        for item in relevant_knowledge:
            knowledge = item['knowledge']
            similarity = item['similarity']
            
            if knowledge.get('type') == 'custom':
                 response_parts.append(f"<div class='custom-info bg-gray-50 p-4 rounded-lg mb-3'><p>{knowledge['text']}</p></div>")
            
            elif knowledge['type'] == 'herb':
                herb_info = f"""
                <div class="herb-info bg-green-50 p-4 rounded-lg mb-3">
                    <h4 class="font-bold text-green-800">{knowledge['name']} ({knowledge['sanskrit_name']})</h4>
                    <p><strong>Scientific Name:</strong> {knowledge['scientific_name']}</p>
                    <p><strong>Description:</strong> {knowledge['description']}</p>
                    <p><strong>Taste:</strong> {knowledge['rasa']} | <strong>Energy:</strong> {knowledge['virya']}</p>
                    <p><strong>Dosage:</strong> {knowledge['dosage']}</p>
                    <p><strong>Preparation:</strong> {knowledge['preparation_method']}</p>
                    {f'<p><strong>Contraindications:</strong> {knowledge["contraindications"]}</p>' if knowledge['contraindications'] else ''}
                </div>
                """
                response_parts.append(herb_info)
                herbs_mentioned.append(knowledge['name'])
                
            elif knowledge['type'] == 'symptom':
                symptom_info = f"""
                <div class="symptom-info bg-blue-50 p-4 rounded-lg mb-3">
                    <h4 class="font-bold text-blue-800">{knowledge['name']}</h4>
                    <p><strong>Category:</strong> {knowledge['category']}</p>
                    <p><strong>Associated Dosha:</strong> {knowledge['associated_dosha']}</p>
                    <p><strong>Description:</strong> {knowledge['description']}</p>
                </div>
                """
                response_parts.append(symptom_info)
                symptoms_mentioned.append(knowledge['name'])
                
            elif knowledge['type'] == 'prakriti':
                prakriti_info = f"""
                <div class="prakriti-info bg-purple-50 p-4 rounded-lg mb-3">
                    <h4 class="font-bold text-purple-800">{knowledge['constitution_type']}</h4>
                    <p><strong>Dominant Dosha:</strong> {knowledge['dominant_dosha']}</p>
                    <p><strong>Characteristics:</strong> {knowledge['characteristics']}</p>
                    <p><strong>Common Ailments:</strong> {knowledge['common_ailments']}</p>
                    <p><strong>Recommended Lifestyle:</strong> {knowledge['recommended_lifestyle']}</p>
                </div>
                """
                response_parts.append(prakriti_info)
                prakriti_types.append(knowledge['constitution_type'])
                
            elif knowledge['type'] == 'relationship':
                relationship_info = f"""
                <div class="relationship-info bg-yellow-50 p-4 rounded-lg mb-3">
                    <h4 class="font-bold text-yellow-800">{knowledge['herb_name']} for {knowledge['symptom_name']}</h4>
                    <p><strong>Effectiveness:</strong> {knowledge['effectiveness_score']}/1.00</p>
                    <p><strong>Dosage:</strong> {knowledge['dosage_for_symptom']}</p>
                    <p><strong>Preparation:</strong> {knowledge['preparation_method']}</p>
                    <p><strong>Treatment Duration:</strong> {knowledge['duration_of_treatment']}</p>
                </div>
                """
                response_parts.append(relationship_info)
        
        # Create a comprehensive response
        response = "<p>Based on your query, here's what I found:</p>"
        
        if response_parts:
            response += "".join(response_parts)
        
        # Add recommendations if relevant
        if herbs_mentioned and symptoms_mentioned:
            response += f"<p class='mt-3'><strong>Recommendation:</strong> Based on the symptoms you mentioned, {', '.join(herbs_mentioned)} might be helpful. However, please consult with an Ayurvedic practitioner for personalized advice.</p>"
        elif herbs_mentioned:
            response += f"<p class='mt-3'><strong>Note:</strong> {', '.join(herbs_mentioned)} has the properties mentioned above. Please consult with an Ayurvedic practitioner for proper dosage and personalized advice.</p>"
        
        return response
    
    def get_response(self, query):
        """Get RAG response for user query"""
        try:
            # Find relevant knowledge
            relevant_knowledge = self._find_relevant_knowledge(query, top_k=5)
            
            # Generate response using retrieved knowledge
            response = self._generate_rag_response(query, relevant_knowledge)
            
            return response
            
        except Exception as e:
            print(f"Error generating RAG response: {e}")
            return "I'm sorry, I encountered an error while processing your request. Please try again."

# Initialize the RAG chatbot service
rag_chatbot_service = RAGChatbotService()

def get_rag_chatbot_response(query):
    """Get RAG chatbot response for a query"""
    return rag_chatbot_service.get_response(query)
